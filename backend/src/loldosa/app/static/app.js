/* LoLDosa — 학습 루프: 연습 목표 → 게임 전 브리핑 → 경기 복기(목표 체크) → 개념 학습 → 다음 목표 */
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const STAGE_KO = { planning: "선픽 의도 표시", banning: "밴 단계", pre_my_pick: "내 픽 전", post_my_pick: "내 픽 확정", final: "전원 확정" };
const LEVEL_KO = { basic: "기초", intermediate: "중급", advanced: "심화" };
const POS = { TOP: "탑", JUNGLE: "정글", MIDDLE: "미드", BOTTOM: "원딜", UTILITY: "서폿" };
let ddragon = "";
let evidence = {};

async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || `오류 ${r.status}`);
  return data;
}
const icon = (key) => (key && ddragon ? `https://ddragon.leagueoflegends.com/cdn/${ddragon}/img/champion/${key}.png` : "");
const imgTag = (key, cls = "") => `<img class="${cls}" src="${icon(key)}" alt="" onerror="this.style.visibility='hidden'">`;

/* ---------------- 탭 ---------------- */
document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => showTab(b.dataset.tab)));
function showTab(name) {
  document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("active", x.dataset.tab === name));
  document.querySelectorAll(".tabpane").forEach((p) => p.classList.toggle("active", p.id === `tab-${name}`));
  if (name === "home") loadHome();
  if (name === "brief") idleFocus();
  if (name === "review") loadMatches();
  if (name === "settings") loadSettings();
  if (name === "learn") loadLearn();
  window.scrollTo(0, 0);
}
const showEv = $("show-ev");
showEv.checked = localStorage.getItem("showEv") === "1";
document.body.classList.toggle("show-ev", showEv.checked);
showEv.onchange = () => { localStorage.setItem("showEv", showEv.checked ? "1" : "0"); document.body.classList.toggle("show-ev", showEv.checked); };

/* ---------------- 개념 사전 + 용어 툴팁 ---------------- */
let learnIndex = null;
let concepts = {};      // id -> {title, summary, ...}
let aliasList = [];     // [[alias, id]] 긴 것부터

async function ensureLearn(force = false) {
  if (learnIndex && !force) return learnIndex;
  learnIndex = await api("/api/learn");
  concepts = Object.fromEntries(learnIndex.concepts.map((c) => [c.id, c]));
  aliasList = [];
  for (const c of learnIndex.concepts) for (const a of [c.title, ...(c.aliases || [])]) if (a && a.length >= 2) aliasList.push([a, c.id]);
  aliasList.sort((a, b) => b[0].length - a[0].length);
  return learnIndex;
}

/** 텍스트를 escape 하고, 개념 용어에 툴팁을 단다 (개념당 처음 한 번만). */
function linkify(text) {
  let html = esc(text);
  if (!aliasList.length) return html;
  const used = new Set();
  const marks = [];
  for (const [alias, id] of aliasList) {
    if (used.has(id)) continue;
    const a = esc(alias);
    const idx = html.indexOf(a);
    if (idx < 0 || marks.some(([s, e]) => idx < e && idx + a.length > s)) continue;
    marks.push([idx, idx + a.length, id]);
    used.add(id);
  }
  marks.sort((x, y) => y[0] - x[0]);
  for (const [s, e, id] of marks) html = `${html.slice(0, s)}<span class="term" data-c="${id}">${html.slice(s, e)}</span>${html.slice(e)}`;
  return html;
}
document.addEventListener("mouseover", (ev) => {
  const t = ev.target.closest(".term");
  const tip = $("term-tip");
  if (!t) { tip.classList.add("hidden"); return; }
  const c = concepts[t.dataset.c];
  if (!c) return;
  const r = t.getBoundingClientRect();
  tip.innerHTML = `<b>${esc(c.title)}</b> <span class="muted">${esc(c.en || "")}</span><div>${esc(c.summary || "")}</div><div class="muted">눌러서 자세히 배우기</div>`;
  tip.style.left = `${Math.max(8, Math.min(r.left, window.innerWidth - 330))}px`;
  tip.style.top = `${r.bottom + 6 + window.scrollY}px`;
  tip.classList.remove("hidden");
});
document.addEventListener("click", (ev) => {
  const t = ev.target.closest(".term");
  if (t) openConcept(t.dataset.c);
});

function evChips(ids, pool = evidence) {
  return (ids || []).map((id) => {
    const e = pool[id];
    if (!e) return "";
    const tip = `${e.text}\n— ${e.source}${e.confidence ? ` · 신뢰도 ${e.confidence}` : ""}`;
    const cls = e.confidence === "낮음" ? "low" : e.confidence === "높음" ? "high" : "";
    const label = `${e.games != null ? `n=${e.games}` : id}${e.url ? " ↗" : ""}`;
    if (e.url) return `<a class="ev ${cls}" href="${esc(e.url)}" target="_blank" rel="noopener" data-tip="${esc(tip)}">${label}</a>`;
    return `<span class="ev ${cls}" data-tip="${esc(tip)}">${label}</span>`;
  }).join("");
}

/** 개념을 그 자리에서 펼쳐 보여주는 '왜?' 블록 */
function whyBlock(conceptIds) {
  const list = (conceptIds || []).map((c) => (typeof c === "string" ? c : c.id)).filter((id) => concepts[id]);
  if (!list.length) return "";
  const body = list.map((id) => `<div class="why-item"><b>${esc(concepts[id].title)}</b> — ${esc(concepts[id].summary || "")}
      <button class="link" onclick="openConcept('${id}')">자세히 배우기 →</button></div>`).join("");
  return `<details class="why"><summary>왜?</summary>${body}</details>`;
}

/* ---------------- 홈 (학습 대시보드) ---------------- */
function dotsHtml(history) {
  return history.slice().reverse().map((x) =>
    `<span class="dot-big ${x.status}" title="${esc(x.date || "")} ${esc(x.champion || "")}: ${esc(x.value)}"></span>`).join("");
}

async function loadHome() {
  await ensureLearn().catch(() => {});
  const h = await api("/api/home");
  if (!h.onboarded) return renderOnboarding(h, 1);
  $("onboarding").classList.add("hidden");
  const f = h.focus;
  const hist = f ? f.history.filter((x) => x.status !== "na") : [];
  const passN = hist.filter((x) => x.status === "pass").length;
  const focusCard = f ? `
    <div class="focus-card">
      <div class="label">지금 연습 중인 목표</div>
      <h2>${esc(f.title)}</h2>
      <div class="goal">🎯 ${esc(f.goal || "")}</div>
      <p>${linkify(f.summary || "")}</p>
      ${f.how && f.how.length ? `<ol class="how">${f.how.map((x) => `<li>${linkify(x)}</li>`).join("")}</ol>` : ""}
      <div class="trend"><span class="muted">최근 경기 (왼쪽이 오래된 경기)</span>
        <div>${hist.length ? dotsHtml(hist) : '<span class="muted">아직 기록이 없어요. 게임을 하고 \'경기 복기\'에서 불러오세요.</span>'}</div>
        ${hist.length ? `<div class="rate">${hist.length}경기 중 <b>${passN}</b>번 달성</div>` : ""}</div>
      <div class="row"><button class="primary" onclick="openConcept('${f.id}')">개념 다시 보기</button>
        <button class="ghost" onclick="pickFocus()">목표 바꾸기</button></div>
    </div>` : `<div class="focus-card empty-focus"><h2>연습 목표를 하나 정해 보세요</h2>
      <p>한 번에 하나만 연습하는 게 가장 빨라요. 목표를 정하면 게임 전 브리핑 맨 위에 나오고, 경기 후 복기에서 지켰는지 체크해요.</p>
      <button class="primary" onclick="pickFocus()">목표 고르기</button></div>`;
  const skills = h.skills.map((s) => {
    const rate = s.total ? s.pass / s.total : null;
    return `<div class="skill" onclick="openConcept('${s.id}')">
      <div class="skill-top"><b>${esc(s.title)}</b>${f && s.id === f.id ? '<span class="pill on">연습 중</span>' : ""}</div>
      <div class="bar"><i style="width:${rate == null ? 0 : Math.max(4, Math.round(rate * 100))}%" class="${rate == null ? "" : rate >= 0.7 ? "good" : rate >= 0.4 ? "mid" : "bad"}"></i></div>
      <div class="muted">${rate == null ? "아직 측정 전" : `최근 ${s.total}경기 중 ${s.pass}번 달성`}</div></div>`;
  }).join("");
  const todo = [];
  if (!h.stats_ready) todo.push("터미널에서 <code>uv run loldosa update</code> 로 고티어 데이터를 먼저 모으세요.");
  if (!h.riot_id) todo.push(`<a href="#" onclick="showTab('settings');return false">설정</a>에서 Riot ID를 입력하세요.`);
  if (h.riot_id && !h.games_tracked) todo.push(`<a href="#" onclick="showTab('review');return false">경기 복기</a>에서 최근 경기를 불러오면 실력 지도가 채워져요.`);
  if (h.suggest && (!f || h.suggest.id !== f.id)) todo.push(`가장 약한 부분은 <b>${esc(h.suggest.title)}</b>이에요 (최근 ${h.suggest.total}경기 중 ${h.suggest.pass}번 달성). <a href="#" onclick="setFocus('${h.suggest.id}');return false">이걸 목표로 하기</a>`);
  $("home").innerHTML = `
    <div class="home-grid">
      <div>${focusCard}
        ${todo.length ? `<div class="panel"><h3 class="sec">다음에 할 일</h3><ul class="todo">${todo.map((t) => `<li>${t}</li>`).join("")}</ul></div>` : ""}
        <div class="panel loop"><h3 class="sec">LoLDosa 쓰는 법</h3>
          <ol><li><b>연습 목표 하나</b>를 정해요 (홈)</li><li>챔피언 선택 때 <b>게임 전 브리핑</b>에서 목표와 이번 판 플랜을 읽어요</li>
          <li>게임이 끝나면 <b>경기 복기</b>에서 목표를 지켰는지 확인해요</li><li>못 지켰다면 <b>개념 학습</b>에서 다시 보고 퀴즈로 확인해요</li></ol></div>
      </div>
      <div>
        <div class="panel"><h3 class="sec">내 실력 지도 <span class="muted">경기 기록으로 잰 개념별 달성률 · 누르면 개념으로</span></h3><div class="skills">${skills}</div></div>
        ${h.recommended.length ? `<div class="panel"><h3 class="sec">복기에서 자주 지적된 개념</h3>${h.recommended.map((r) =>
          `<button class="chip-link" onclick="openConcept('${r.id}')">📘 ${esc(r.title)} · ${r.count}경기</button>`).join("")}</div>` : ""}
      </div>
    </div>`;
}

async function setFocus(id) {
  await api("/api/focus", { method: "PUT", body: JSON.stringify({ concept: id }) });
  closeModal();
  if ($("tab-home").classList.contains("active")) loadHome();
}
window.setFocus = setFocus;

async function pickFocus() {
  const h = await api("/api/home");
  const rows = h.skills.map((s) => {
    const c = concepts[s.id] || {};
    const rate = s.total ? `최근 ${s.total}경기 중 ${s.pass}번 달성` : "아직 측정 전";
    return `<div class="pick-focus" onclick="setFocus('${s.id}')"><b>${esc(s.title)}</b>
      <div class="muted">🎯 ${esc(s.goal)} · ${rate}</div><div>${esc(c.summary || "")}</div></div>`;
  }).join("");
  openModal(`<h2>연습 목표 고르기</h2><p class="muted">경기 기록으로 지켰는지 잴 수 있는 개념만 고를 수 있어요. 약한 것부터 위에 있어요.</p>${rows}`);
}
window.pickFocus = pickFocus;

function openModal(html) {
  let m = $("modal");
  if (!m) { m = document.createElement("div"); m.id = "modal"; m.className = "modal"; document.body.appendChild(m); }
  m.innerHTML = `<div class="modal-box"><button class="modal-x" onclick="closeModal()">✕</button>${html}</div>`;
  m.classList.remove("hidden");
}
function closeModal() { const m = $("modal"); if (m) m.classList.add("hidden"); }
window.closeModal = closeModal;

/* 처음 쓰는 사람: Riot ID → 첫 목표 */
async function renderOnboarding(h, step) {
  $("home").innerHTML = "";
  const box = $("onboarding");
  box.classList.remove("hidden");
  const steps = ["Riot ID", "첫 연습 목표"];
  const head = `<div class="steps">${steps.map((s, i) => `<span class="${i + 1 === step ? "on" : ""}">${i + 1}. ${s}</span>`).join("")}</div>`;
  if (step === 1) {
    box.innerHTML = `${head}<h1>반가워요! 정글 실력을 같이 올려봐요</h1>
      <p>LoLDosa는 <b>게임 전 브리핑 → 경기 복기 → 개념 학습</b>을 반복하면서, 한 번에 한 가지씩 실력을 올리도록 도와줘요.</p>
      <div class="field"><label>내 Riot ID</label><input id="ob-riot" placeholder="닉네임#태그" value="${esc(h.riot_id || "")}"></div>
      <button class="primary" id="ob-next">다음</button> <button class="ghost" id="ob-skip">나중에</button>`;
    $("ob-next").onclick = async () => {
      const v = $("ob-riot").value.trim();
      if (v) await api("/api/settings", { method: "PUT", body: JSON.stringify({ riot_id: v }) });
      renderOnboarding(h, 2);
    };
    $("ob-skip").onclick = () => renderOnboarding(h, 2);
  } else {
    await ensureLearn().catch(() => {});
    const starters = ["full-clear", "recall-timing", "jungle-tracking", "objective-setup"];
    box.innerHTML = `${head}<h1>첫 연습 목표를 골라요</h1>
      <p>처음이라면 아래 중 하나를 추천해요. 경기를 몇 판 복기하면 약한 부분을 찾아 다시 추천해 드려요.</p>
      ${starters.filter((id) => concepts[id]).map((id) => `<div class="pick-focus" onclick="setFocus('${id}')"><b>${esc(concepts[id].title)}</b>
        <div>${esc(concepts[id].summary || "")}</div></div>`).join("")}
      <button class="ghost" onclick="setFocus('')">목표 없이 시작</button>`;
  }
}

/* ---------------- 게임 전 브리핑 ---------------- */
function renderTeams(st) {
  const row = (x) => `<li class="${x.me ? "me" : ""} ${x.picking ? "picking" : ""}">
      <span class="pos">${esc(x.position)}</span>${x.key ? imgTag(x.key) : `<img alt="">`}
      <span class="${x.hovering ? "hover" : ""}">${esc(x.name || "—")}${x.me ? " (나)" : ""}</span></li>`;
  $("allies").innerHTML = st.allies.map(row).join("");
  $("enemies").innerHTML = st.enemies.map(row).join("");
  const bans = (list) => list.map((b) => (b.key ? imgTag(b.key) : "")).join("");
  $("ally-bans").innerHTML = bans(st.ally_bans);
  $("enemy-bans").innerHTML = bans(st.enemy_bans);
  $("side-badge").textContent = st.side === "blue" ? "블루" : "레드";
  $("side-badge").className = `side ${st.side}`;
}

function pickCard(r, { score = true } = {}) {
  const why = r.reasons.length > 1 ? r.reasons[1].text : (r.reasons[0] ? r.reasons[0].text : "");
  return `<div class="pick" onclick="this.classList.toggle('open')">
    <div class="pick-top">${imgTag(r.key)}<span class="pick-name">${esc(r.name)}${r.in_pool ? '<span class="pool-badge">내 폭</span>' : ""}</span>
      ${score ? `<span class="pick-score">${(r.score * 100).toFixed(1)}%</span>` : ""}</div>
    <div class="pick-why">${esc(why)}</div>
    <ul>${r.reasons.map((i) => `<li>${esc(i.text)}${evChips(i.evidence)}</li>`).join("")}</ul></div>`;
}

function focusBanner(f) {
  if (!f) return "";
  return `<div class="label">이번 판 연습 목표</div><div class="fb-title">${esc(f.title)} — 🎯 ${esc(f.goal || "")}</div>
    ${f.how && f.how.length ? `<ol class="how">${f.how.map((x) => `<li>${linkify(x)}</li>`).join("")}</ol>` : ""}`;
}

function onBriefing(msg) {
  ddragon = msg.ddragon || ddragon;
  const st = msg.state, b = msg.briefing;
  evidence = Object.fromEntries(b.evidence.map((e) => [e.id, e]));
  $("brief-idle").classList.add("hidden");
  $("brief").classList.remove("hidden");
  $("ended-banner").classList.add("hidden");
  $("stage").textContent = STAGE_KO[b.stage] || b.stage;
  $("matchup-title").textContent = b.my_champion_name ? `${b.my_champion_name}${b.enemy_jungler_name ? ` vs ${b.enemy_jungler_name}` : ""}` : "";
  $("scope").textContent = b.scope_label ? `데이터: ${b.scope_label}` : "";
  const focus = msg.focus || currentFocus;
  $("focus-banner").classList.toggle("hidden", !focus);
  $("focus-banner").innerHTML = focusBanner(focus);
  $("notes").innerHTML = b.notes.map((n) => `<div class="note">${linkify(n)}</div>`).join("");
  renderTeams(st);
  const show = b.picks.length || b.bans.length;
  $("picks-box").classList.toggle("hidden", !show);
  $("picks").innerHTML = b.picks.map((r) => pickCard(r)).join("") || `<span class="muted">추천할 후보가 없습니다</span>`;
  $("picks-outside-wrap").classList.toggle("hidden", !b.picks_outside.length);
  $("picks-outside").innerHTML = b.picks_outside.map((r) => pickCard(r)).join("");
  $("bans-wrap").classList.toggle("hidden", !b.bans.length);
  $("bans").innerHTML = b.bans.map((r) => pickCard(r, { score: false })).join("");
  $("pool-hint").textContent = b.picks.some((r) => r.in_pool) ? "내 챔프폭 안에서 추천 · 카드를 누르면 이유" : "설정에서 챔프폭을 고르면 그 안에서 추천해요";
  $("plan-box").classList.toggle("hidden", !b.plan.length);
  $("plan").innerHTML = b.plan.map((p) => `<li><span class="tag ${p.title === "주의" ? "warn" : ""}">${esc(p.title)}</span>
      <div><div class="txt">${linkify(p.text)}${evChips(p.evidence)}</div>${whyBlock(p.concepts)}</div></li>`).join("");
  $("cards").innerHTML = b.cards.map((c) => `<article class="card"><div class="card-head"><span class="card-title">${esc(c.title)}</span>
      <span class="card-headline">${linkify(c.headline)}</span></div>
      <ul class="card-items">${c.items.map((i) => `<li class="${i.kind}">${linkify(i.text)}${evChips(i.evidence)}</li>`).join("")}</ul></article>`).join("");
  if (!["post_my_pick", "final"].includes(b.stage)) $("ai").classList.add("hidden");
}

function renderAI(msg) {
  $("ai").classList.remove("hidden");
  $("ai-status").textContent = "";
  if (msg.status === "running") { $("ai-headline").textContent = "근거를 바탕으로 정리 중… (10~20초)"; $("ai-points").innerHTML = ""; return; }
  if (msg.status !== "ok") { $("ai-headline").textContent = "AI 코치를 사용할 수 없습니다"; $("ai-points").innerHTML = ""; $("ai-status").textContent = msg.message || ""; return; }
  $("ai-headline").innerHTML = linkify(msg.headline);
  $("ai-points").innerHTML = msg.points.map((p) => `<li><span class="phase">${esc(p.phase)}</span>${linkify(p.text)}${evChips(p.evidence)}</li>`).join("");
}

async function loadStatus() {
  try {
    const s = await (await fetch("/api/status")).json();
    ddragon = s.ddragon || ddragon;
    $("pill-lcu").textContent = s.replay ? "데모 재생" : s.lcu ? "클라이언트 연결" : "클라이언트 꺼짐";
    $("pill-lcu").className = `pill ${s.lcu ? "on" : "off"}`;
    $("status-line").textContent = s.stats && s.stats.built_at ? `고티어 데이터 갱신 ${s.stats.built_at.replace("T", " ").slice(0, 16)}` : "고티어 데이터 없음 → loldosa update";
  } catch (e) { /* 재시작 중 */ }
}
let currentFocus = null;
async function idleFocus() {
  try {
    const h = await api("/api/home");
    currentFocus = h.focus;
    $("idle-focus").innerHTML = h.focus ? `<div class="focus-banner idle">${focusBanner(h.focus)}</div>` : "";
    $("focus-banner").classList.toggle("hidden", !h.focus);
    $("focus-banner").innerHTML = focusBanner(h.focus);
  } catch (e) { /* noop */ }
}

function connect() {
  const ws = new WebSocket(`ws://${location.host}/ws`);
  ws.onopen = () => { $("pill-ws").textContent = "연결됨"; $("pill-ws").className = "pill on"; loadStatus(); };
  ws.onclose = () => { $("pill-ws").textContent = "재연결 중"; $("pill-ws").className = "pill off"; setTimeout(connect, 1500); };
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.type === "briefing") onBriefing(msg);
    else if (msg.type === "ai") renderAI(msg);
    else if (msg.type === "ended") $("ended-banner").classList.remove("hidden");
  };
}

/* ---------------- 경기 복기 ---------------- */
let champMap = {};
let currentMatch = null;
const champName = (id) => (champMap[id] ? champMap[id].name : `#${id}`);
const champKey = (id) => (champMap[id] ? champMap[id].key : "");
async function ensureChamps() {
  if (Object.keys(champMap).length) return;
  const list = await api("/api/champions");
  champMap = Object.fromEntries(list.map((c) => [c.id, c]));
  window._champList = list;
}

function renderMatchList(list) {
  $("match-list").innerHTML = list.map((m) => `<li class="match ${m.win ? "win" : "loss"} ${m.match_id === currentMatch ? "active" : ""}" data-id="${m.match_id}">
      ${imgTag(champKey(m.champion_id))}
      <div><div class="m1">${esc(champName(m.champion_id))} <span class="muted">${esc(POS[m.position] || m.position)}</span></div>
      <div class="m2">${m.kills}/${m.deaths}/${m.assists} · ${String(m.game_start).slice(5, 16).replace("T", " ")}</div>
      ${m.focus_status && m.focus_status !== "na" ? `<div class="m2 ${m.focus_status}">연습 목표 ${m.focus_status === "pass" ? "달성 ✓" : "미달 ✗"}</div>` : ""}</div>
      <span class="res">${m.win ? "승" : "패"}</span></li>`).join("") || `<li class="muted" style="padding:12px">불러온 경기가 없어요. 위에 Riot ID를 넣고 '경기 불러오기'를 누르세요.</li>`;
  document.querySelectorAll(".match").forEach((li) => (li.onclick = () => openReview(li.dataset.id)));
}
async function loadMatches() {
  await Promise.all([ensureChamps(), ensureLearn().catch(() => {})]);
  const s = await api("/api/settings");
  if (!$("riot-id").value) $("riot-id").value = s.riot_id || "";
  renderMatchList(await api("/api/review/matches"));
}
$("review-sync").onclick = async () => {
  const btn = $("review-sync");
  btn.disabled = true;
  $("review-status").textContent = "경기를 받고 분석하는 중… (경기당 2~3초)";
  try {
    await ensureChamps();
    const list = await api("/api/review/sync", { method: "POST", body: JSON.stringify({ riot_id: $("riot-id").value, count: +$("review-count").value }) });
    renderMatchList(list);
    $("review-status").textContent = `${list.length}경기 · 홈의 실력 지도가 갱신됐어요`;
    if (list.length && !currentMatch) openReview(list[0].match_id);
  } catch (e) { $("review-status").textContent = e.message; } finally { btn.disabled = false; }
};

function minimap(rv) {
  const S = 340, M = 14870;
  const px = (x) => (x / M) * S, py = (y) => S - (y / M) * S;
  const path = (pts, color) => pts.length ? `<polyline points="${pts.map((p) => `${px(p[1])},${py(p[2])}`).join(" ")}" fill="none" stroke="${color}" stroke-width="2" stroke-opacity=".75"/>`
    + pts.map((p) => `<circle cx="${px(p[1])}" cy="${py(p[2])}" r="${p[0] <= 4 ? 7 : 5}" fill="${color}" fill-opacity=".85"/><text x="${px(p[1])}" y="${py(p[2]) + 3}" font-size="8" text-anchor="middle" fill="#000">${p[0]}</text>`).join("") : "";
  const marks = rv.moments.filter((m) => m.x != null && m.t <= 660 && ["death", "enemy_gank", "objective"].includes(m.kind)).map((m) => {
    const c = m.kind === "objective" ? (m.good ? "#3ccf91" : "#ffb547") : "#ff5f66";
    return `<text x="${px(m.x)}" y="${py(m.y) + 5}" font-size="14" text-anchor="middle" fill="${c}"><title>${esc(m.text)}</title>${m.kind === "objective" ? "◆" : "✕"}</text>`;
  }).join("");
  return `<div class="minimap"><img src="https://ddragon.leagueoflegends.com/cdn/${ddragon}/img/map/map11.png" alt="" onerror="this.remove()">
    <svg viewBox="0 0 ${S} ${S}">${path(rv.paths.enemy_jungler, "#ff5f66")}${path(rv.paths.me, "#f0d79a")}${marks}</svg></div>
    <div class="legend"><span><i style="background:#f0d79a"></i>나 (숫자=분)</span><span><i style="background:#ff5f66"></i>적 정글</span><span style="color:#ff5f66">✕ 데스·적 갱</span><span style="color:#ffb547">◆ 적 오브젝트</span><span style="color:#3ccf91">◆ 우리 오브젝트</span></div>`;
}

async function openReview(id) {
  currentMatch = id;
  document.querySelectorAll(".match").forEach((li) => li.classList.toggle("active", li.dataset.id === id));
  const box = $("review-detail");
  box.innerHTML = `<p class="muted">분석 중…</p>`;
  try {
    const rv = await api(`/api/review/${id}`);
    const pool = Object.fromEntries(rv.evidence.map((e) => [e.id, e]));
    const sm = rv.summary;
    const focus = rv.checks.find((c) => c.focus);
    const kl = rv.key_lesson;
    const keyCard = kl ? `<div class="key-lesson">
        <div class="label">이 경기에서 하나만 배운다면</div>
        <h2>${esc(kl.lesson.title)}</h2>
        <p>${linkify(kl.lesson.text)}${evChips(kl.lesson.evidence, pool)}</p>
        <div class="concept-box"><div class="label">관련 개념 · ${esc(kl.concept.title)}</div><p>${linkify(kl.concept.summary || "")}</p>
          ${kl.concept.how && kl.concept.how.length ? `<ol class="how">${kl.concept.how.slice(0, 3).map((x) => `<li>${linkify(x)}</li>`).join("")}</ol>` : ""}
          <div class="row"><button class="primary" onclick="openConcept('${kl.concept.id}')">개념 배우기</button>
          ${rv.checks.some((c) => c.concept === kl.concept.id) && !(focus && focus.concept === kl.concept.id) ? `<button class="ghost" onclick="setFocusFromReview('${kl.concept.id}')">다음 판 연습 목표로</button>` : ""}</div></div>
      </div>` : (rv.is_jungle ? `<div class="key-lesson good"><h2>눈에 띄는 큰 실수가 없었어요 👍</h2><p>아래 체크에서 지킨 것과 놓친 것을 확인해 보세요.</p></div>` : "");
    const checks = rv.checks.length ? `<h3 class="sec">개념 체크 <span class="muted">경기 기록으로 측정 · 누르면 개념으로</span></h3><div class="checks">${rv.checks.filter((c) => c.status !== "na").map((c) =>
      `<div class="check ${c.status} ${c.focus ? "focus" : ""}" onclick="openConcept('${c.concept}')"><span class="ic">${c.status === "pass" ? "✓" : "✗"}</span>
        <div><b>${esc(c.title)}</b>${c.focus ? ' <span class="pill on">연습 목표</span>' : ""}<div class="muted">${esc(c.value)}</div></div></div>`).join("")}</div>` : "";
    const others = rv.lessons.filter((l) => !kl || l.title !== kl.lesson.title).slice(0, 4).map((l) => `<div class="lesson sev${Math.min(l.severity, 3)}"><h4>${esc(l.title)}</h4>
        <p>${linkify(l.text)}${evChips(l.evidence, pool)}</p>${whyBlock(l.concepts)}</div>`).join("");
    const strengths = rv.strengths.map((l) => `<span class="strength">✓ ${esc(l.title)}</span>`).join("");
    const metrics = rv.metrics.map((m) => `<tr><td>${linkify(m.label)}</td><td class="${m.verdict}">${esc(m.mine)}</td><td>${esc(m.bench)}</td><td>${evChips(m.evidence, pool)}</td></tr>`).join("");
    const moments = rv.moments.map((m) => `<li class="${m.good === true ? "good" : m.good === false ? "bad" : ""} ${m.kind}">${linkify(m.text)}</li>`).join("");
    box.innerHTML = `
      <div class="rv-head">${imgTag(sm.key)}<div>
        <h2>${esc(sm.champion)} <span class="${sm.win ? "res-win" : "res-loss"}">${sm.win ? "승리" : "패배"}</span></h2>
        <div class="muted">${esc(sm.position)} · ${esc(sm.side)} · ${esc(sm.kda)} · ${esc(sm.duration)} · ${esc(sm.date)}${sm.enemy_jungler ? ` · 상대 정글 ${esc(sm.enemy_jungler)}` : ""}</div></div>
        ${focus && focus.status !== "na" ? `<div class="focus-result ${focus.status}">연습 목표 <b>${esc(focus.title)}</b><br>${focus.status === "pass" ? "달성 ✓" : "미달 ✗"} · ${esc(focus.value)}</div>` : ""}</div>
      ${rv.notes.map((n) => `<div class="note">${linkify(n)}</div>`).join("")}
      ${keyCard}
      ${checks}
      ${others ? `<h3 class="sec">그 밖에 고칠 점</h3>${others}` : ""}
      ${strengths ? `<h3 class="sec">잘한 점</h3><div class="strengths">${strengths}</div>` : ""}
      <div id="rv-ai"><button class="ghost" id="rv-ai-btn">🤖 AI 복기 코칭 받기</button></div>
      <details class="more"><summary>경기 흐름 보기 <span class="muted">(10분 동선 · 주요 순간 · 고티어 비교표)</span></summary>
        <div class="rv-grid"><div>${minimap(rv)}</div><div><ul class="moments">${moments}</ul></div></div>
        ${metrics ? `<table class="metrics"><tr><th>항목</th><th>나</th><th>고티어 (${esc(rv.scope_label)})</th><th></th></tr>${metrics}</table>` : ""}
      </details>`;
    $("rv-ai-btn").onclick = async () => {
      const btn = $("rv-ai-btn");
      btn.disabled = true; btn.textContent = "정리 중… (10~20초)";
      try {
        const r = await api(`/api/review/${id}/ai`, { method: "POST" });
        $("rv-ai").innerHTML = r.status === "ok" ? `<div class="ai"><div class="ai-head"><span class="badge">AI 복기</span>${linkify(r.headline)}</div>
          <ol>${r.points.map((p) => `<li><span class="phase">${esc(p.phase)}</span>${linkify(p.text)}${evChips(p.evidence, pool)}</li>`).join("")}</ol></div>`
          : `<p class="muted">${esc(r.message || "AI 코치를 사용할 수 없습니다")}</p>`;
      } catch (e) { $("rv-ai").innerHTML = `<p class="muted">${esc(e.message)}</p>`; }
    };
  } catch (e) { box.innerHTML = `<p class="muted">${esc(e.message)}</p>`; }
}
async function setFocusFromReview(id) {
  await api("/api/focus", { method: "PUT", body: JSON.stringify({ concept: id }) });
  openModal(`<h2>다음 판 연습 목표로 정했어요</h2><p>게임 전 브리핑 맨 위에 이 목표가 나오고, 경기 후 복기에서 지켰는지 체크해요.</p>
    <button class="primary" onclick="closeModal();showTab('home')">홈에서 보기</button>`);
}
window.setFocusFromReview = setFocusFromReview;

/* ---------------- 개념 학습 ---------------- */
async function loadLearn(force = true) {
  const idx = await ensureLearn(force);
  const q = $("learn-search").value.trim().replace(/\s/g, "").toLowerCase();
  const match = (c) => !q || [c.title, c.en, c.summary, c.id, ...(c.aliases || [])].join(" ").replace(/\s/g, "").toLowerCase().includes(q);
  $("learn-reco").innerHTML = idx.recommended.length ? `<div class="reco"><h4>추천 학습 · 복기에서 지적됨</h4>
      ${idx.recommended.map((r) => `<div class="learn-item" onclick="openConcept('${r.id}')">${esc(r.title)}<span class="lv">${r.count}경기</span></div>`).join("")}</div>` : "";
  $("learn-list").innerHTML = idx.categories.map((cat) => {
    const items = idx.concepts.filter((c) => c.category === cat.id && match(c));
    if (!items.length) return "";
    return `<div class="learn-cat">${esc(cat.name)}</div>` + items.map((c) => {
      const qz = idx.quiz[c.id];
      const dot = qz && qz.total && qz.correct / qz.total >= 0.8 ? "done" : idx.read[c.id] ? "read" : "";
      return `<div class="learn-item" data-id="${c.id}" onclick="openConcept('${c.id}')"><span class="dot ${dot}"></span>${esc(c.title)}
        ${c.measurable ? '<span class="lv" title="경기 기록으로 측정 가능">🎯</span>' : `<span class="lv">${esc(LEVEL_KO[c.level] || "")}</span>`}</div>`;
    }).join("");
  }).join("") || `<p class="muted">개념 데이터가 없습니다.</p>`;
}
$("learn-search").oninput = () => loadLearn(false);

function listBlock(title, arr, ordered = false) {
  if (!arr || !arr.length) return "";
  const tag = ordered ? "ol" : "ul";
  return `<h3>${title}</h3><${tag}>${arr.map((x) => `<li>${linkify(x)}</li>`).join("")}</${tag}>`;
}

async function openConcept(id) {
  if (!$("tab-learn").classList.contains("active")) {
    document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("active", x.dataset.tab === "learn"));
    document.querySelectorAll(".tabpane").forEach((p) => p.classList.toggle("active", p.id === "tab-learn"));
    await loadLearn(false);
  }
  $("term-tip").classList.add("hidden");
  const c = await api(`/api/learn/${encodeURIComponent(id)}`);
  document.querySelectorAll("#learn-list .learn-item").forEach((el) => el.classList.toggle("active", el.dataset.id === id));
  const nums = (c.numbers || []).length ? `<h3>수치 (현재 시즌)</h3><table class="numbers">${c.numbers.map((n) =>
      `<tr><td>${esc(n.label)}</td><td>${esc(n.value)}</td><td class="nnote">${esc(n.note || "")}</td></tr>`).join("")}</table>` : "";
  const quiz = (c.quiz || []).map((q, qi) => `<div class="quiz" data-q="${qi}"><div class="q">Q${qi + 1}. ${esc(q.q)}</div>
      ${q.choices.map((ch, ci) => `<button class="choice" data-c="${ci}">${esc(ch)}</button>`).join("")}
      <div class="explain hidden">${esc(q.explain || "")}</div></div>`).join("");
  const hist = (c.history || []).length ? `<div class="trend"><span class="muted">내 최근 경기</span><div>${dotsHtml(c.history)}</div></div>` : "";
  const goalBox = c.goal ? `<div class="goal-box"><div>🎯 <b>경기에서 이렇게 측정해요</b>: ${esc(c.goal)}</div>${hist}
      ${c.is_focus ? '<span class="pill on">지금 연습 중</span>' : `<button class="primary" onclick="setFocus('${c.id}').then(() => openConcept('${c.id}'))">이걸 연습 목표로</button>`}</div>` : "";
  const cat = (learnIndex.categories.find((x) => x.id === c.category) || {}).name || "";
  $("learn-detail").innerHTML = `
    <div class="crumb">${esc(cat)} · ${esc(LEVEL_KO[c.level] || "")}${c.flagged ? ` · 내 복기에서 ${c.flagged}경기 지적됨` : ""}</div>
    <h1>${esc(c.title)}<span class="en">${esc(c.en || "")}</span></h1>
    <div class="summary">${esc(c.summary || "")}</div>
    ${goalBox}
    ${c.definition ? `<h3>무엇인가요</h3><p>${linkify(c.definition)}</p>` : ""}
    ${c.why ? `<h3>왜 중요한가요</h3><p>${linkify(c.why)}</p>` : ""}
    ${listBlock("이렇게 하세요", c.how, true)}
    ${listBlock("정글러라면", c.jungler)}
    ${listBlock("자주 하는 실수", c.mistakes)}
    ${quiz ? `<h3>이해했는지 확인해요</h3>${quiz}` : ""}
    ${nums}
    ${(c.related || []).length ? `<h3>같이 보면 좋은 개념</h3>${c.related.map((r) => `<button class="chip-link" onclick="openConcept('${r.id}')">📘 ${esc(r.title)}</button>`).join("")}` : ""}
    ${(c.sources || []).length ? `<details class="more"><summary>출처</summary><ul class="sources">${c.sources.map((s) =>
        `<li>${s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title || s.url)}</a>` : esc(s.title)}${s.note ? ` <span class="muted">(${esc(s.note)})</span>` : ""}</li>`).join("")}</ul></details>` : ""}`;
  document.querySelectorAll("#learn-detail .quiz").forEach((box) => {
    const q = c.quiz[+box.dataset.q];
    box.querySelectorAll(".choice").forEach((btn) => (btn.onclick = async () => {
      if (box.dataset.done) return;
      box.dataset.done = "1";
      const ok = +btn.dataset.c === q.answer;
      btn.classList.add(ok ? "right" : "wrong");
      box.querySelector(`.choice[data-c="${q.answer}"]`).classList.add("right");
      box.querySelector(".explain").classList.remove("hidden");
      await api(`/api/learn/${encodeURIComponent(id)}/quiz`, { method: "POST", body: JSON.stringify({ correct: ok }) });
    }));
  });
  window.scrollTo(0, 0);
}
window.openConcept = openConcept;
window.showTab = showTab;

/* ---------------- 설정 ---------------- */
let pool = new Set();
async function loadSettings() {
  await ensureChamps();
  const s = await api("/api/settings");
  $("set-riot-id").value = s.riot_id || "";
  $("set-bucket").value = s.my_bucket || "platinum";
  $("set-ai").checked = !!s.ai_enabled;
  pool = new Set(s.champion_pool || []);
  renderChampGrid();
}
function renderChampGrid() {
  const q = $("champ-search").value.trim().replace(/\s/g, "").toLowerCase();
  const list = (window._champList || []).filter((c) => !q || c.name.replace(/\s/g, "").toLowerCase().includes(q) || c.key.toLowerCase().includes(q));
  $("champ-grid").innerHTML = list.map((c) => `<div class="champ ${pool.has(c.id) ? "sel" : ""}" data-id="${c.id}" title="${c.jungle_games ? `고티어 정글 ${c.jungle_games}판` : ""}">${imgTag(c.key)}${esc(c.name)}</div>`).join("");
  document.querySelectorAll(".champ").forEach((el) => (el.onclick = () => {
    const id = +el.dataset.id;
    pool.has(id) ? pool.delete(id) : pool.add(id);
    el.classList.toggle("sel");
    $("pool-count").textContent = `${pool.size}명 선택`;
  }));
  $("pool-count").textContent = `${pool.size}명 선택`;
}
$("champ-search").oninput = renderChampGrid;
$("save-settings").onclick = async () => {
  try {
    await api("/api/settings", { method: "PUT", body: JSON.stringify({ riot_id: $("set-riot-id").value.trim(), my_bucket: $("set-bucket").value, ai_enabled: $("set-ai").checked, champion_pool: [...pool] }) });
    $("settings-status").textContent = "저장했어요. 다음 챔피언 선택부터 적용됩니다.";
    $("riot-id").value = $("set-riot-id").value.trim();
  } catch (e) { $("settings-status").textContent = e.message; }
};

/* ---------------- 시작 ---------------- */
connect();
loadStatus().then(() => ensureLearn().catch(() => {})).then(() => { loadHome().catch(() => {}); idleFocus(); });
setInterval(loadStatus, 15000);
