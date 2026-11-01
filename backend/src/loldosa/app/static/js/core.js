/* 공통: API, 상태, 라우터, 시트·토스트·스켈레톤, 용어 툴팁, 숫자 표기.
 * 디자인 근거는 docs/DESIGN.md 의 규칙 번호(B·H·R·L·S)로 주석에 남긴다. */

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export const state = { ddragon: "", concepts: {}, aliases: [], learn: null, champs: {}, champList: [], status: {}, home: null };

export async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || `잠시 뒤 다시 시도해 주세요 (오류 ${r.status})`);
  return data;
}
export const post = (path, body) => api(path, { method: "POST", body: JSON.stringify(body || {}) });
export const put = (path, body) => api(path, { method: "PUT", body: JSON.stringify(body || {}) });

/* ---------- 숫자 표기 (B7: 게임 시계 형식, 천 단위 쉼표, 변화량 부호) ---------- */
export const mmss = (t) => (t == null ? "-" : `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`);
export const comma = (n) => (n == null ? "-" : Math.round(n).toLocaleString("ko-KR"));
export const signed = (n) => (n == null ? "-" : `${n >= 0 ? "+" : ""}${Math.round(n).toLocaleString("ko-KR")}`);
export const pct = (x) => (x == null ? "-" : `${Math.round(x * 100)}%`);
export const josa = (word, pair = "이가") => {
  const ch = String(word || "").trim().slice(-1);
  const code = ch.charCodeAt(0) - 0xac00;
  const has = code >= 0 && code <= 11171 ? code % 28 !== 0 : false;
  return `${word}${has ? pair[0] : pair[1]}`;
};

/* ---------- 챔피언 ---------- */
export const icon = (key) => (key && state.ddragon ? `https://ddragon.leagueoflegends.com/cdn/${state.ddragon}/img/champion/${key}.png` : "");
export const champImg = (key, alt = "") => (key ? `<img src="${icon(key)}" alt="${esc(alt)}" loading="lazy" onerror="this.remove()">` : "");
export async function ensureChamps() {
  if (state.champList.length) return;
  state.champList = await api("/api/champions");
  state.champs = Object.fromEntries(state.champList.map((c) => [c.id, c]));
}
export const champName = (id) => state.champs[id]?.name || "";
export const champKey = (id) => state.champs[id]?.key || "";

/* ---------- 개념 사전 + 용어 툴팁 (L1: 낯선 말은 그 자리에서 풀어 준다) ---------- */
export async function ensureLearn(force = false) {
  if (state.learn && !force) return state.learn;
  state.learn = await api("/api/learn");
  state.concepts = Object.fromEntries(state.learn.concepts.map((c) => [c.id, c]));
  state.aliases = [];
  for (const c of state.learn.concepts) for (const a of [c.title, ...(c.aliases || [])]) if (a && a.length >= 2) state.aliases.push([a, c.id]);
  state.aliases.sort((a, b) => b[0].length - a[0].length);
  return state.learn;
}
/** 글을 escape 하고, 개념 용어(개념당 처음 한 번)에 점선 밑줄을 단다. */
export function linkify(text) {
  let html = esc(text);
  const used = new Set(), marks = [];
  for (const [alias, id] of state.aliases) {
    if (used.has(id)) continue;
    const a = esc(alias), i = html.indexOf(a);
    if (i < 0 || marks.some(([s, e]) => i < e && i + a.length > s)) continue;
    marks.push([i, i + a.length, id]); used.add(id);
  }
  marks.sort((x, y) => y[0] - x[0]);
  for (const [s, e, id] of marks) html = `${html.slice(0, s)}<span class="term" data-c="${id}" tabindex="0" role="button">${html.slice(s, e)}</span>${html.slice(e)}`;
  return html;
}
let tipEl = null;
function showTip(t) {
  const c = state.concepts[t.dataset.c];
  if (!c) return;
  tipEl = tipEl || Object.assign(document.createElement("div"), { className: "tip" });
  tipEl.innerHTML = `<b>${esc(c.title)}</b><div style="margin-top:4px">${esc(c.summary || "")}</div><div class="sub" style="margin-top:6px">눌러서 자세히 보기</div>`;
  document.body.appendChild(tipEl);
  const r = t.getBoundingClientRect();
  tipEl.style.left = `${Math.max(8, Math.min(r.left, innerWidth - 316))}px`;
  tipEl.style.top = `${r.bottom + 8 + scrollY}px`;
}
document.addEventListener("mouseover", (e) => { const t = e.target.closest(".term"); if (t) showTip(t); else tipEl?.remove(); });
document.addEventListener("focusin", (e) => { const t = e.target.closest?.(".term"); if (t) showTip(t); });
document.addEventListener("click", (e) => { const t = e.target.closest(".term"); if (t) { tipEl?.remove(); go(`#/learn/${t.dataset.c}`); } });

/* ---------- 근거 표시: 기본 숨김 (B2: 우리만 알면 되는 정보는 접는다), 설정에서 켜기 ---------- */
export function evChips(ids, pool = {}) {
  return (ids || []).map((id) => {
    const e = pool[id];
    if (!e) return "";
    const tip = `${e.text} — ${e.source}${e.confidence ? ` · 신뢰도 ${e.confidence}` : ""}`;
    return `<span class="ev" title="${esc(tip)}">${e.games != null ? `${comma(e.games)}판` : "근거"}</span>`;
  }).join("");
}

/* ---------- 라우터: 해시 경로 → 화면 (뒤로 가기 동작) ---------- */
const routes = [];
export const route = (re, render) => routes.push([re, render]);
export const go = (hash) => { if (location.hash === hash) render(); else location.hash = hash; };
export async function render() {
  const h = location.hash || "#/home";
  for (const [re, fn] of routes) {
    const m = h.match(re);
    if (m) {
      $$(".nav-item").forEach((n) => n.classList.toggle("on", h.startsWith(n.dataset.href)));
      closeSheet(); tipEl?.remove();
      window.scrollTo(0, 0);
      await fn($("#view"), ...m.slice(1));
      return;
    }
  }
  go("#/home");
}
addEventListener("hashchange", render);

/* ---------- 시트 (H4·§1.6: 결정·세부는 별도 층) ---------- */
export function openSheet(html, { wide = false, onClose } = {}) {
  closeSheet();
  const dim = document.createElement("div");
  dim.className = "dim"; dim.id = "sheet";
  dim.innerHTML = `<div class="sheet ${wide ? "wide" : ""}" role="dialog" aria-modal="true" tabindex="-1">
    <button class="close" aria-label="닫기" data-close>✕</button>${html}</div>`;
  dim.addEventListener("click", (e) => { if (e.target === dim || e.target.closest("[data-close]")) { closeSheet(); onClose?.(); } });
  document.body.appendChild(dim);
  // 입력칸이 있으면 바로 입력, 없으면 시트 자체에 포커스 (첫 버튼으로 가면 아래로 스크롤돼서 제목이 가려짐)
  setTimeout(() => ($(".sheet input", dim) || $(".sheet", dim))?.focus({ preventScroll: true }), 50);
  return $(".sheet", dim);
}
export function closeSheet() { $("#sheet")?.remove(); }
addEventListener("keydown", (e) => { if (e.key === "Escape") closeSheet(); });

/* ---------- 토스트: 결과는 짧게 알리고 사라진다 ---------- */
export function toast(msg) {
  $(".toast")?.remove();
  const t = Object.assign(document.createElement("div"), { className: "toast", textContent: msg, role: "status" });
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2600);
}

/* ---------- 스켈레톤 (B4: 스피너 대신 모양) ---------- */
export const skeleton = (n = 3) => `<div class="sk big"></div><div class="sk line" style="width:60%"></div>${'<div class="sk card"></div>'.repeat(n)}`;

/* ---------- 작은 조각들 ---------- */
export const chev = `<svg class="chev" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
export function row({ lead = "", title, sub = "", end = "", href = "", attrs = "", cls = "" }) {
  const tag = href ? "a" : attrs.includes("data-") ? "button" : "div";
  return `<${tag} class="row ${cls}" ${href ? `href="${href}"` : ""} ${attrs}>
    ${lead ? `<div class="lead">${lead}</div>` : ""}
    <div class="mid"><div class="title">${title}</div>${sub ? `<div class="sub">${sub}</div>` : ""}</div>
    ${end ? `<div class="end">${end}</div>` : ""}${href || tag === "button" ? chev : ""}</${tag}>`;
}
export const badge = (text, color = "") => `<span class="badge ${color}">${esc(text)}</span>`;
export function empty({ em = "🌱", title, desc = "", action = "" }) {
  return `<div class="empty"><div class="em" aria-hidden="true">${em}</div><h3>${title}</h3>${desc ? `<p>${desc}</p>` : ""}${action}</div>`;
}
export const GROUP_KO = { pro: "프로", challenger: "챌린저", apex: "마스터+", diamond: "다이아", emerald: "에메랄드", platinum: "플래티넘" };
export const POS_KO = { TOP: "탑", JUNGLE: "정글", MIDDLE: "미드", BOTTOM: "원딜", UTILITY: "서폿" };

/* ---------- 리플레이 열기 (공통 흐름) ---------- */
/* 보기만 하면 남는 게 적어서(수동 시청), 볼 것 하나를 같이 준다 */
const taskBox = (task) => (task ? `<div class="look" style="margin-top:16px"><div class="eyebrow">보면서 할 일</div><div class="body">${esc(task)}</div></div>` : "");
export async function openReplay(matchId, t, task = "") {
  const sh = openSheet(`<h2>리플레이를 여는 중이에요</h2><p class="body">롤 클라이언트에서 ${mmss(t)} 조금 앞으로 이동해요. 길면 1~2분 걸려요.</p>
    ${taskBox(task)}<div class="sk line" style="width:70%;margin-top:20px"></div>`);
  try {
    const r = await post(`/api/replay/${matchId}`, { t });
    sh.innerHTML = `<button class="close" aria-label="닫기" data-close>✕</button>
      <h2>${r.status === "ok" ? "리플레이를 열었어요" : "리플레이를 열지 못했어요"}</h2><p class="body">${esc(r.message || "")}</p>${r.status === "ok" ? taskBox(task) : ""}
      <div class="btn-row end"><button class="btn m grey" data-close>닫기</button></div>`;
  } catch (e) {
    sh.innerHTML = `<button class="close" aria-label="닫기" data-close>✕</button><h2>리플레이를 열지 못했어요</h2>
      <p class="body">${esc(e.message)}. 롤 클라이언트가 켜져 있는지 확인해 주세요.</p><div class="btn-row end"><button class="btn m grey" data-close>닫기</button></div>`;
  }
}
window.__openReplay = openReplay;
