/* LoLDosa — 학습 루프: 연습 목표 → 게임 전 브리핑 → 경기 복기(목표 체크) → 개념 학습 → 다음 목표 */
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const STAGE_KO = { planning: "픽 미리 찍기", banning: "밴 단계", pre_my_pick: "내 픽 전", post_my_pick: "내 픽 확정", final: "전원 확정" };
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
      <div class="goal">🎯 ${esc(f.goal || "")}</div>${f.note ? `<div class="note">${esc(f.note)}</div>` : ""}
      <p>${linkify(f.summary || "")}</p>
      ${f.how && f.how.length ? `<ol class="how">${f.how.map((x) => `<li>${linkify(x)}</li>`).join("")}</ol>` : ""}
      <div class="trend"><span class="muted">최근 경기 (왼쪽이 오래된 경기)</span>
        <div>${hist.length ? dotsHtml(hist) : '<span class="muted">아직 기록이 없어요. 게임을 하고 \'경기 복기\'에서 불러오세요.</span>'}</div>
        ${hist.length ? `<div class="rate">최근 ${hist.length}판 중 <b>${passN}</b>번 지킴</div>` : ""}</div>
      <div class="row"><button class="primary" onclick="openConcept('${f.id}')">설명 다시 보기</button>
        <button class="ghost" onclick="pickFocus()">목표 바꾸기</button></div>
    </div>` : `<div class="focus-card empty-focus"><h2>연습 목표를 하나 정해 보세요</h2>
      <p>한 번에 하나만 연습하는 게 가장 빨라요. 목표를 정하면 게임 전 브리핑 맨 위에 나오고, 경기 후 복기에서 지켰는지 체크해요.</p>
      <button class="primary" onclick="pickFocus()">목표 고르기</button></div>`;
  const skills = h.skills.map((s) => {
    const rate = s.total ? s.pass / s.total : null;
    return `<div class="skill" onclick="openConcept('${s.id}')">
      <div class="skill-top"><b>${esc(s.title)}</b>${f && s.id === f.id ? '<span class="pill on">연습 중</span>' : ""}
        ${s.mastery && s.mastery.score != null ? `<span class="mastery ${s.mastery.score >= 75 ? "good" : s.mastery.score >= 45 ? "mid" : "bad"}" title="숙련도: 경기 체크·판단 훈련·퀴즈를 합친 점수">${s.mastery.score}</span>` : ""}</div>
      <div class="bar"><i style="width:${rate == null ? 0 : Math.max(4, Math.round(rate * 100))}%" class="${rate == null ? "" : rate >= 0.7 ? "good" : rate >= 0.4 ? "mid" : "bad"}"></i></div>
      <div class="muted">${rate == null ? "아직 기록 없음" : `최근 ${s.total}판 중 ${s.pass}번 지킴${s.total < 5 ? " · 판 수가 적어 참고만" : ""}`}</div></div>`;
  }).join("");
  const todo = [];
  if (!h.stats_ready) todo.push("터미널에서 <code>uv run loldosa update</code> 로 고티어 데이터를 먼저 모으세요.");
  if (!h.riot_id) todo.push(`<a href="#" onclick="showTab('settings');return false">설정</a>에서 Riot ID를 입력하세요.`);
  if (h.riot_id && !h.games_tracked) todo.push(`<a href="#" onclick="showTab('review');return false">경기 복기</a>에서 최근 경기를 불러오면 개념별 달성률이 채워져요.`);
  if (h.suggest && (!f || h.suggest.id !== f.id)) todo.push(`가장 약한 부분은 <b>${esc(h.suggest.title)}</b>이에요 (최근 ${h.suggest.total}판 중 ${h.suggest.pass}번 지킴). <a href="#" onclick="setFocus('${h.suggest.id}');return false">이걸 목표로 하기</a>`);
  const due = h.due ? `<div class="panel due"><div><b>오늘의 복습 ${h.due}개</b><div class="muted">틀렸던 판단 장면과 약한 개념을 잊을 때쯤 다시 풀어요 (1·2·4·8·16일 간격)</div></div>
      <button class="primary" onclick="startReview()">복습 시작</button></div>` : "";
  const ef = h.effect;
  const pct0 = (a, b) => (b ? `${Math.round((a / b) * 100)}%` : "-");
  const effect = ef ? `<div class="panel"><h3 class="sec">효과 리포트 <span class="muted">목표를 정한 ${esc(ef.since.slice(0, 10))} 전후</span></h3>
      <table class="metrics"><tr><th></th><th>정하기 전 (최근 ${ef.before.games}판)</th><th>정한 뒤 (${ef.after.games}판)</th></tr>
      <tr><td>목표 지킨 비율</td><td>${pct0(ef.before.focus_pass, ef.before.focus_total)}</td><td>${pct0(ef.after.focus_pass, ef.after.focus_total)}</td></tr>
      <tr><td>승률</td><td>${pct0(ef.before.wins, ef.before.games)}</td><td>${pct0(ef.after.wins, ef.after.games)}</td></tr>
      <tr><td>랭크</td><td>${esc(ef.rank_start)}</td><td>${esc(ef.rank_now)}${ef.rank_delta != null ? ` (${ef.rank_delta >= 0 ? "+" : ""}${ef.rank_delta}점)` : ""}</td></tr></table>
      <p class="muted">${ef.after.games < 5 ? "목표를 정한 뒤 판 수가 적어서 아직은 참고만 하세요." : "판 수가 쌓일수록 믿을 만해져요. 랭크 점수는 디비전 100점·티어 400점 기준이에요."}</p></div>` : "";
  $("home").innerHTML = `
    ${h.rank ? `<div class="rank-line">현재 랭크 <b>${esc(h.rank)}</b></div>` : ""}
    <div id="gap-panel"></div>
    <div class="home-grid">
      <div>${due}${focusCard}${effect}
        ${todo.length ? `<div class="panel"><h3 class="sec">다음에 할 일</h3><ul class="todo">${todo.map((t) => `<li>${t}</li>`).join("")}</ul></div>` : ""}
        <div class="panel loop"><h3 class="sec">LoLDosa 쓰는 법</h3>
          <ol><li><b>연습 목표 하나</b>를 정해요 (홈)</li><li>챔피언 선택 때 <b>게임 전 브리핑</b>에서 목표와 이번 판 플랜을 읽어요</li>
          <li>게임이 끝나면 <b>경기 복기</b>에서 목표를 지켰는지 확인해요</li><li>못 지켰다면 <b>개념 학습</b>에서 다시 보고 퀴즈로 확인해요</li></ol></div>
      </div>
      <div>
        <div class="panel"><h3 class="sec">내 개념별 달성률 <span class="muted">경기 기록 기준 · 누르면 설명 보기</span></h3><div class="skills">${skills}</div></div>
        ${h.recommended.length ? `<div class="panel"><h3 class="sec">복기에서 자주 지적된 개념</h3>${h.recommended.map((r) =>
          `<button class="chip-link" onclick="openConcept('${r.id}')">📘 ${esc(r.title)} · ${r.count}판</button>`).join("")}</div>` : ""}
      </div>
    </div>`;
  CHECKABLE = new Set(h.skills.map((x) => x.id));
  loadGap();
}

/* ---------- 챌린저까지의 거리 ---------- */
const GROUP_KO = { pro: "프로", challenger: "챌린저", apex: "마스터+", platinum: "플래티넘", diamond: "다이아", emerald: "에메랄드" };
async function loadGap() {
  const box = $("gap-panel");
  if (!box) return;
  let g;
  try { g = await api("/api/gap"); } catch (e) { box.innerHTML = ""; return; }
  if (!g.ready) {
    box.innerHTML = `<div class="panel gap"><h3 class="sec">챌린저까지 가장 큰 차이</h3><p class="muted">${esc(g.reason)}</p></div>`;
    return;
  }
  const bar = (p) => `<div class="gap-bar"><div style="width:${Math.max(0, Math.min(100, p))}%"></div><span class="tick plat">플래티넘</span><span class="tick chal">챌린저</span></div>`;
  const trend = g.progress_before != null ? ` <span class="muted">(앞쪽 판 ${g.progress_before}점 → 최근 ${g.progress_now}점)</span>` : "";
  const item = (x, i) => `<div class="gap-item">
      <div class="gap-rank">${i + 1}</div>
      <div class="gap-main"><b>${esc(x.label)}</b>
        <div class="gap-nums">나 <b>${esc(x.mine_text)}</b>${x.before_text ? ` <span class="muted">(전 ${esc(x.before_text)})</span>` : ""} · 플래티넘 ${esc(x.groups_text.platinum || "-")} · 챌린저 <b>${esc(x.groups_text.challenger || "-")}</b> · 프로 ${esc(x.groups_text.pro || "-")}</div>
        <div class="gap-drill">다음 판: ${esc(x.drill)}</div>
        <div class="gap-step">이번 주 목표: <b>${esc(x.step_text)}</b> <span class="muted">(챌린저까지 남은 거리의 1/3 · 판이 쌓이면 다시 계산돼요)</span></div>
        ${x.concept === "communication-pings" ? `<div class="muted small-note">핑 횟수 자체가 목표는 아니에요. 핑을 치려면 미니맵을 보고 있어야 해서, 고수일수록 많이 치는 거예요. 의미 없는 핑 연타는 오히려 팀을 흔들어요.</div>` : ""}
        ${x.examples && x.examples.length ? `<div class="gap-ex"><span class="muted">프로가 하는 거 보기 (롤 클라이언트에서 리플레이가 그 시점으로 열려요):</span>
          ${x.examples.map((e) => `<button class="ghost small" onclick="openReplay('${e.match_id}', ${Math.round(e.t)})">🎬 ${esc(e.player)} · ${esc(e.champion)} · ${esc(e.value_text)}</button>`).join("")}</div>` : ""}
        <div class="row"><button class="ghost small" onclick="openConcept('${x.concept}')">개념 보기</button>
        ${CHECKABLE.has(x.concept) ? `<button class="ghost small" onclick="setFocus('${x.concept}')">연습 목표로</button>` : ""}</div></div>
      <div class="gap-power" title="고수와 플래티넘을 가르는 힘 (0.5 = 못 가름, 1 = 완벽히 가름)">가르는 힘 ${Math.round((x.auc - 0.5) * 200)}</div></div>`;
  box.innerHTML = `<div class="panel gap">
    <div class="gap-head"><h3 class="sec">챌린저까지 가장 큰 차이 <span class="muted">내 최근 정글 ${g.games}판 · 프로·챌린저·마스터+ ${(g.groups.pro || 0) + (g.groups.challenger || 0) + (g.groups.apex || 0)}판과 플래티넘 ${g.groups.platinum}판을 실제로 비교해 찾은 지표만 써요 · 내 값은 챔피언 차이를 보정한 중앙값</span></h3>
      <div class="gap-score"><div class="big">${g.progress}<small>점</small></div><div class="muted">플래티넘 0 · 챌린저 100${trend}</div>${bar(g.progress)}</div></div>
    ${g.gaps.length ? g.gaps.map(item).join("") : `<p>검증된 지표에서 챌린저 중앙값과 큰 차이가 없어요. 👍</p>`}
    ${g.by_champion && g.by_champion.length > 1 ? `<div class="gap-champs"><span class="muted">챔피언별 진행도 (3판 이상):</span> ${g.by_champion.map((c) =>
      `<span class="gap-champ">${imgTag(c.key)} ${esc(c.name)} <b>${c.progress}점</b> <span class="muted">${c.wins}승 ${c.games - c.wins}패</span></span>`).join("")}
      <div class="muted">점수가 높은 챔피언일수록 고수처럼 플레이하고 있다는 뜻이에요. 랭크에선 이 챔피언들을 먼저 고르세요.</div></div>` : ""}
    ${g.strengths.length ? `<div class="gap-strength">이미 챌린저 수준: ${g.strengths.map((x) => `<span class="strength">✓ ${esc(x.label)} ${esc(x.mine_text)}</span>`).join(" ")}</div>` : ""}
  </div>`;
}
let CHECKABLE = new Set();

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
    const rate = s.total ? `최근 ${s.total}판 중 ${s.pass}번 지킴` : "아직 기록 없음";
    return `<div class="pick-focus" onclick="setFocus('${s.id}')"><b>${esc(s.title)}</b>
      <div class="muted">🎯 ${esc(s.goal)} · ${rate}</div><div>${esc(c.summary || "")}</div></div>`;
  }).join("");
  openModal(`<h2>연습 목표 고르기</h2><p class="muted">경기 기록으로 지켰는지 체크할 수 있는 개념만 고를 수 있어요. 약한 것부터 위에 있어요.</p>${rows}`);
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
    <div class="pick-top">${imgTag(r.key)}<span class="pick-name">${esc(r.name)}${r.in_pool ? '<span class="pool-badge">내 폭</span>' : ""}${myChamps[r.champion_id] ? `<span class="pool-badge me" title="내 최근 ${myChamps[r.champion_id].games}판 기준 챌린저 진행도">내 ${myChamps[r.champion_id].progress}점</span>` : ""}</span>
      ${score ? `<span class="pick-score">${(r.score * 100).toFixed(1)}%</span>` : ""}</div>
    <div class="pick-why">${esc(why)}</div>
    <ul>${r.reasons.map((i) => `<li>${esc(i.text)}${evChips(i.evidence)}</li>`).join("")}</ul></div>`;
}

function focusBanner(f, practice) {
  if (!f && !practice) return "";
  const graded = f && f.graded !== false;
  const focusPart = graded ? `<div class="label">이번 판 연습 목표</div><div class="fb-title">${esc(f.title)} — 🎯 ${esc(f.goal || "")}</div>
    ${f.how && f.how.length ? `<ol class="how">${f.how.map((x) => `<li>${linkify(x)}</li>`).join("")}</ol>` : ""}` : "";
  const gapPart = practice ? `<div class="fb-gap"><div class="label">챌린저와 가장 큰 차이</div>
    <b>${esc(practice.label)}</b> · 나 ${esc(practice.mine_text)} → 챌린저 ${esc(practice.target_text)}
    <div class="fb-drill">이번 판: ${esc(practice.drill)}</div></div>` : "";
  const stale = f && !graded ? `<div class="muted">지금 연습 목표(${esc(f.title)})는 실제 경기 검증을 통과하지 못해서 채점하지 않아요. 홈에서 새 목표를 골라 주세요.</div>` : "";
  return focusPart + gapPart + stale;
}

let myChamps = {};
function onBriefing(msg) {
  ddragon = msg.ddragon || ddragon;
  myChamps = msg.my_champs || myChamps;
  const st = msg.state, b = msg.briefing;
  evidence = Object.fromEntries(b.evidence.map((e) => [e.id, e]));
  $("brief-idle").classList.add("hidden");
  $("brief").classList.remove("hidden");
  $("ended-banner").classList.add("hidden");
  $("stage").textContent = STAGE_KO[b.stage] || b.stage;
  $("matchup-title").textContent = b.my_champion_name ? `${b.my_champion_name}${b.enemy_jungler_name ? ` vs ${b.enemy_jungler_name}` : ""}` : "";
  $("scope").textContent = b.scope_label ? `데이터: ${b.scope_label}` : "";
  const focus = msg.focus || currentFocus;
  const practice = msg.practice || currentPractice;
  $("focus-banner").classList.toggle("hidden", !focus && !practice);
  $("focus-banner").innerHTML = focusBanner(focus, practice);
  $("notes").innerHTML = b.notes.map((n) => `<div class="note">${linkify(n)}</div>`).join("");
  renderTeams(st);
  const show = b.picks.length || b.bans.length;
  $("picks-box").classList.toggle("hidden", !show);
  $("picks").innerHTML = b.picks.map((r) => pickCard(r)).join("") || `<span class="muted">추천할 챔피언이 없어요</span>`;
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
  if (!pathState || JSON.stringify(pathState.paths) !== JSON.stringify(b.paths)) renderPaths(b.paths);
}

/* ---------- 첫 6분 시간표 (정확한 기록만) ---------- */
const REGION_SAY = { own_jungle: "우리 정글", enemy_jungle: "상대 정글", river: "강가", top: "탑 라인", mid: "미드 라인", bot: "봇 라인", base: "본진" };
const MONSTER_SAY = { DRAGON: "드래곤", HORDE: "공허 유충", RIFTHERALD: "협곡의 전령", BARON_NASHOR: "바론" };
let pathState = null;
const mmssJs = (t) => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`;
function eventSay(e) {
  if (e.kind === "recall") return e.t < 150 ? "상점 구매 (2분 전 구매라 귀환인지는 확실하지 않아요)" : "귀환 (상점 구매 시각)";
  if (e.kind === "death_back") return "죽고 부활해서 템 구매";
  if (e.kind === "death") return `죽음 · ${REGION_SAY[e.where] || ""}`;
  if (e.kind === "kill") return `킬 · ${REGION_SAY[e.where] || ""}`;
  if (e.kind === "assist") return `킬 도움 · ${REGION_SAY[e.where] || ""}`;
  if (e.kind === "objective") return `${e.ours ? "우리" : "상대"} 팀 ${MONSTER_SAY[e.monster] || e.monster} 처치`;
  return e.kind;
}
function timelineRows(rec) {
  const rows = rec.minutes.map((p) => ({ t: p.m * 60, html: `<span class="tl-min">${p.m}:00</span> 먹은 캠프 <b>${p.camps}개</b> <span class="muted">· 그 순간 위치: ${REGION_SAY[p.region] || p.region}</span>` }));
  for (const e of rec.events) rows.push({ t: e.t, html: `<span class="tl-ev ${e.kind}">${mmssJs(e.t)}</span> <b>${esc(eventSay(e))}</b>` });
  return rows.sort((a, b) => a.t - b.t).map((r) => `<li>${r.html}</li>`).join("");
}
function renderPaths(paths) {
  const box = $("paths-box");
  if (!paths || !paths.mine || !paths.mine.length) { box.classList.add("hidden"); return; }
  box.classList.remove("hidden");
  pathState = { paths, style: 0 };
  $("paths-styles").innerHTML = paths.mine.map((p, i) => `<button class="ghost small ${i === 0 ? "on" : ""}" data-i="${i}">${esc(p.label)} · 고티어 ${p.games}판</button>`).join("");
  document.querySelectorAll("#paths-styles button").forEach((b) => (b.onclick = () => {
    pathState.style = +b.dataset.i;
    document.querySelectorAll("#paths-styles button").forEach((x) => x.classList.toggle("on", x === b));
    drawPaths();
  }));
  drawPaths();
}
function drawPaths() {
  const mine = pathState.paths.mine[pathState.style], enemy = pathState.paths.enemy;
  $("paths-table").innerHTML = `<div class="tl-grid">
    <div><h4>나 · ${esc(mine.label)}</h4><ol class="timeline">${timelineRows(mine)}</ol></div>
    ${enemy ? `<div><h4>상대 · ${esc(enemy.name)}</h4><ol class="timeline">${timelineRows(enemy)}</ol></div>` : ""}</div>`;
}

function renderAI(msg) {
  $("ai").classList.remove("hidden");
  $("ai-status").textContent = "";
  if (msg.status === "running") { $("ai-headline").textContent = "근거 보고 정리하는 중… (10~20초)"; $("ai-points").innerHTML = ""; return; }
  if (msg.status !== "ok") { $("ai-headline").textContent = "AI 코치를 쓸 수 없어요"; $("ai-points").innerHTML = ""; $("ai-status").textContent = msg.message || ""; return; }
  $("ai-headline").innerHTML = linkify(msg.headline);
  $("ai-points").innerHTML = msg.points.map((p) => `<li><span class="phase">${esc(p.phase)}</span>${linkify(p.text)}${evChips(p.evidence)}</li>`).join("");
}

async function loadStatus() {
  try {
    const s = await (await fetch("/api/status")).json();
    ddragon = s.ddragon || ddragon;
    $("pill-lcu").textContent = s.replay ? "데모 재생" : s.lcu ? "클라이언트 연결" : "클라이언트 꺼짐";
    $("pill-lcu").className = `pill ${s.lcu ? "on" : "off"}`;
    $("status-line").textContent = s.stats && s.stats.built_at ? `고티어 데이터 업데이트 ${s.stats.built_at.replace("T", " ").slice(0, 16)}` : "고티어 데이터 없음 → loldosa update";
  } catch (e) { /* 재시작 중 */ }
}
let currentFocus = null, currentPractice = null;
async function idleFocus() {
  try {
    const h = await api("/api/home");
    currentFocus = h.focus; currentPractice = h.practice;
    const any = h.focus || h.practice;
    $("idle-focus").innerHTML = any ? `<div class="focus-banner idle">${focusBanner(h.focus, h.practice)}</div>` : "";
    $("focus-banner").classList.toggle("hidden", !any);
    $("focus-banner").innerHTML = focusBanner(h.focus, h.practice);
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
    else if (msg.type === "postgame") onPostgame(msg);
  };
}

/* ---------------- 게임 끝나면: 이번 판 핵심 하나 ---------------- */
function onPostgame(msg) {
  let box = $("postgame");
  if (!box) { box = document.createElement("div"); box.id = "postgame"; document.body.appendChild(box); }
  const seenKey = `pg:${msg.match_id}:${msg.status}`;
  if (msg.match_id && localStorage.getItem(seenKey)) return;
  const close = `<button class="modal-x" onclick="dismissPostgame('${seenKey}')">✕</button>`;
  if (msg.status !== "ready") {
    box.innerHTML = `<div class="pg-card">${close}<div class="pg-title">${msg.status === "waiting" ? "⏳ " : ""}${esc(msg.message)}</div></div>`;
    return;
  }
  const res = msg.win ? `<span class="res-win">승리</span>` : `<span class="res-loss">패배</span>`;
  box.innerHTML = `<div class="pg-card">${close}
    <div class="pg-title">방금 판 · ${esc(msg.champion || "")} ${res}</div>
    ${msg.focus ? `<div class="pg-focus ${msg.focus.status}">연습 목표 <b>${esc(msg.focus.title)}</b> ${msg.focus.status === "pass" ? "지킴 ✓" : "못 지킴 ✗"}<div class="muted">${esc(msg.focus.value)}</div></div>` : ""}
    ${msg.lesson && msg.lesson.title ? `<div class="pg-lesson"><div class="label">이번 판 핵심 하나</div><b>${esc(msg.lesson.title)}</b><p>${linkify(msg.lesson.text || "")}</p></div>` : `<div class="pg-lesson"><b>눈에 띄는 큰 실수는 없었어요 👍</b></div>`}
    ${msg.gap ? `<div class="pg-gap">챌린저와 차이: <b>${esc(msg.gap.label)}</b> ${esc(msg.gap.mine_text)} (기준 ${esc(msg.gap.threshold_text)}) · ${esc(msg.gap.drill)}</div>` : ""}
    <div class="row"><button class="primary" onclick="openPostgame('${msg.match_id}', '${seenKey}')">자세히 복기하기</button></div></div>`;
  try { if (window.Notification && Notification.permission === "granted") new Notification("LoLDosa · 방금 판 복기", { body: (msg.lesson && msg.lesson.title) || "복기가 준비됐어요" }); } catch (e) {}
}
function dismissPostgame(key) { localStorage.setItem(key, "1"); const b = $("postgame"); if (b) b.innerHTML = ""; }
async function openPostgame(mid, key) {
  dismissPostgame(key);
  showTab("review");
  await ensureChamps().catch(() => {});
  openReview(mid);
}
window.dismissPostgame = dismissPostgame; window.openPostgame = openPostgame;
if (window.Notification && Notification.permission === "default") { try { Notification.requestPermission(); } catch (e) {} }

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
      ${m.focus_status && m.focus_status !== "na" ? `<div class="m2 ${m.focus_status}">연습 목표 ${m.focus_status === "pass" ? "지킴 ✓" : "못 지킴 ✗"}</div>` : ""}</div>
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
  $("review-status").textContent = "경기 불러와서 분석 중… (한 판에 2~3초)";
  try {
    await ensureChamps();
    const list = await api("/api/review/sync", { method: "POST", body: JSON.stringify({ riot_id: $("riot-id").value, count: +$("review-count").value }) });
    renderMatchList(list);
    $("review-status").textContent = `${list.length}경기 · 홈의 개념별 달성률이 업데이트됐어요`;
    if (list.length && !currentMatch) openReview(list[0].match_id);
  } catch (e) { $("review-status").textContent = e.message; } finally { btn.disabled = false; }
};

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
          ${kl.lesson.t != null ? `<button class="ghost" onclick="openReplay('${id}', ${kl.lesson.t})">🎬 리플레이로 보기</button>` : ""}
          ${rv.checks.some((c) => c.concept === kl.concept.id) && !(focus && focus.concept === kl.concept.id) ? `<button class="ghost" onclick="setFocusFromReview('${kl.concept.id}')">다음 판 연습 목표로</button>` : ""}</div></div>
      </div>` : (rv.is_jungle ? `<div class="key-lesson good"><h2>눈에 띄는 큰 실수가 없었어요 👍</h2><p>아래 체크에서 지킨 것과 놓친 것을 확인해 보세요.</p></div>` : "");
    const checks = rv.checks.length ? `<h3 class="sec">목표 체크 <span class="muted">경기 기록으로 체크 · 누르면 설명 보기</span></h3><div class="checks">${rv.checks.filter((c) => c.status !== "na").map((c) =>
      `<div class="check ${c.status} ${c.focus ? "focus" : ""}" onclick="openConcept('${c.concept}')"><span class="ic">${c.status === "pass" ? "✓" : "✗"}</span>
        <div><b>${esc(c.title)}</b>${c.focus ? ' <span class="pill on">연습 목표</span>' : ""}<div class="muted">${esc(c.value)}</div></div></div>`).join("")}</div>
      ${rv.checks.some((c) => c.info) ? `<details class="more"><summary>참고 기록 <span class="muted">(프로·챌린저와 플래티넘 사이에 차이가 없어서 채점하지 않는 항목)</span></summary>
        <ul class="info-checks">${rv.checks.filter((c) => c.info).map((c) => `<li><b>${esc(c.title)}</b> · ${esc(c.info)} <span class="muted">· 통과율 프로 ${Math.round(c.validation.pro * 100)}% / 챌린저 ${Math.round(c.validation.challenger * 100)}% / 플래티넘 ${Math.round(c.validation.platinum * 100)}%</span></li>`).join("")}</ul></details>` : ""}` : "";
    const others = rv.lessons.filter((l) => !kl || l.title !== kl.lesson.title).slice(0, 4).map((l) => `<div class="lesson sev${Math.min(l.severity, 3)}"><h4>${esc(l.title)}</h4>
        <p>${linkify(l.text)}${evChips(l.evidence, pool)}</p>${whyBlock(l.concepts)}</div>`).join("");
    const strengths = rv.strengths.map((l) => `<span class="strength">✓ ${esc(l.title)}</span>`).join("");
    const metrics = rv.metrics.map((m) => `<tr><td>${linkify(m.label)}</td><td class="${m.verdict}">${esc(m.mine)}</td><td>${esc(m.me_avg || "-")}</td><td>${esc(m.target || "-")}</td><td>${esc(m.bench)}</td><td>${evChips(m.evidence, pool)}</td></tr>`).join("");
    const cmp = rv.compare || {};
    const moments = rv.moments.map((m) => `<li class="${m.good === true ? "good" : m.good === false ? "bad" : ""} ${m.kind}">${linkify(m.text)}</li>`).join("");
    box.innerHTML = `
      <div class="rv-head">${imgTag(sm.key)}<div>
        <h2>${esc(sm.champion)} <span class="${sm.win ? "res-win" : "res-loss"}">${sm.win ? "승리" : "패배"}</span></h2>
        <div class="muted">${esc(sm.position)} · ${esc(sm.side)} · ${esc(sm.kda)} · ${esc(sm.duration)} · ${esc(sm.date)}${sm.enemy_jungler ? ` · 상대 정글 ${esc(sm.enemy_jungler)}` : ""}</div></div>
        ${focus && focus.status !== "na" ? `<div class="focus-result ${focus.status}">연습 목표 <b>${esc(focus.title)}</b><br>${focus.status === "pass" ? "지킴 ✓" : "못 지킴 ✗"} · ${esc(focus.value)}</div>` : ""}</div>
      ${rv.notes.map((n) => `<div class="note">${linkify(n)}</div>`).join("")}
      ${keyCard}
      <div id="moments-box"><h3 class="sec">그 순간으로 돌아가기</h3><p class="muted">이 판의 판단 지점을 불러오는 중…</p></div>
      ${checks}
      ${rv.gap && rv.gap.length ? `<h3 class="sec">이번 판 실력 지표 <span class="muted">고수와 플래티넘을 실제로 가르는 지표만 · 기준선 = 고수 4명 중 3명이 넘는 선</span></h3>
        <table class="metrics gap-table"><tr><th>지표</th><th>이번 판</th><th>기준선</th><th>플래티넘</th><th>챌린저</th></tr>
        ${rv.gap.map((x) => `<tr onclick="openConcept('${x.concept}')"><td>${esc(x.label)}</td><td class="${x.ok ? "good" : "bad"}">${esc(x.mine_text)} ${x.ok ? "✓" : "✗"}</td>
          <td>${x.higher_better ? "" : "≤ "}${esc(x.threshold_text)}${x.higher_better ? " 이상" : ""}</td><td>${esc(x.platinum_text)}</td><td>${esc(x.challenger_text)}</td></tr>`).join("")}</table>` : ""}
      ${others ? `<h3 class="sec">그 밖에 고칠 점</h3>${others}` : ""}
      ${strengths ? `<h3 class="sec">잘한 점</h3><div class="strengths">${strengths}</div>` : ""}
      <div id="rv-ai"><button class="ghost" id="rv-ai-btn">🤖 AI 복기 코칭 받기</button></div>
      <details class="more"><summary>경기 기록 보기 <span class="muted">(사건 시간표 · 비교표)</span></summary>
        <h4>정확한 시각이 있는 사건들</h4><ul class="moments">${moments}</ul>
        ${metrics ? `<table class="metrics"><tr><th>항목</th><th>이번 판</th><th>내 최근 평균${cmp.me_games ? ` (${cmp.me_games}판)` : ""}</th><th>다음 티어 ${esc(cmp.target_label || "")}</th><th>고티어 (${esc(rv.scope_label)})</th><th></th></tr>${metrics}</table>` : ""}
      </details>`;
    loadMoments(id);
    $("rv-ai-btn").onclick = async () => {
      const btn = $("rv-ai-btn");
      btn.disabled = true; btn.textContent = "정리 중… (10~20초)";
      try {
        const r = await api(`/api/review/${id}/ai`, { method: "POST" });
        $("rv-ai").innerHTML = r.status === "ok" ? `<div class="ai"><div class="ai-head"><span class="badge">AI 복기</span>${linkify(r.headline)}</div>
          <ol>${r.points.map((p) => `<li><span class="phase">${esc(p.phase)}</span>${linkify(p.text)}${evChips(p.evidence, pool)}</li>`).join("")}</ol></div>`
          : `<p class="muted">${esc(r.message || "AI 코치를 쓸 수 없어요")}</p>`;
      } catch (e) { $("rv-ai").innerHTML = `<p class="muted">${esc(e.message)}</p>`; }
    };
  } catch (e) { box.innerHTML = `<p class="muted">${esc(e.message)}</p>`; }
}
/* ---------- 그 순간으로 돌아가기 (판단 훈련) ---------- */
/** 상황판: 실제 지도 대신 라인 그림 + 글자 라벨. 항상 우리 본진이 왼쪽 아래. */
function snapshotMap(snap, size = 320) {
  const M = 14870, flip = snap.team === 200;
  const X = (x) => ((flip ? M - x : x) / M) * size, Y = (y) => size - ((flip ? M - y : y) / M) * size;
  const S = size, pad = 18;
  const laneSay = (v) => v > 150 ? `우리 +${Math.round(v)}` : v < -150 ? `우리 ${Math.round(v)}` : "비슷";
  const laneCls = (v) => v > 150 ? "win" : v < -150 ? "lose" : "even";
  const L = snap.lanes || {};
  // 라벨 겹침 피하기: 중요한 유닛부터 자리를 잡고, 겹치면 위·아래로 비켜 놓는다.
  const order = [...snap.units].sort((a, b) => (b.me ? 3 : b.enemy_jungler ? 2 : 0) - (a.me ? 3 : a.enemy_jungler ? 2 : 0));
  const chosen = [];
  const boxes = [{ x: pad + 4, y: pad + 3, w: 70, h: 13 }, { x: S / 2 + 8, y: S / 2 - 19, w: 70, h: 13 },
    { x: S - pad - 76, y: S - pad - 17, w: 74, h: 13 }, { x: pad + 2, y: S - pad - 17, w: 50, h: 13 }, { x: S - pad - 50, y: pad + 3, w: 48, h: 13 },
    ...snap.objectives.map((o) => { const w = (o.name.length + o.text.length + 1) * 7; return { x: X(o.x) - w / 2, y: Y(o.y) - 11, w, h: 13 }; })];
  for (const u of snap.units) boxes.push({ x: X(u.x) - 6, y: Y(u.y) - 6, w: 12, h: 12 });  // 점 위에 글자가 덮이지 않게
  for (const u of order) {
    const cls = u.me ? "me" : u.enemy_jungler ? "ejg" : u.ally ? "ally" : "enemy";
    const text = (u.me ? `나 · ${u.name}` : u.enemy_jungler ? `상대 정글 · ${u.name}` : u.name)
      + (u.hp != null && (u.me || u.enemy_jungler) ? ` (체력 ${u.hp}%)` : "");
    const w = text.length * (u.me || u.enemy_jungler ? 9.5 : 8.5), h = 12;
    const cx = X(u.x), cy = Y(u.y);
    let spot = null;
    for (const [dx, dy] of [[8, 4], [8, -9], [8, 17], [-8 - w, 4], [-8 - w, -9], [-8 - w, 17], [8, -22], [8, 30]]) {
      let bx = cx + dx; if (bx + w > S - 2) bx = cx - 8 - w; if (bx < 2) bx = 2;
      const by = cy + dy - 10;
      if (!boxes.some((b) => bx < b.x + b.w && bx + w > b.x && by < b.y + b.h && by + h > b.y)) { spot = { x: bx, y: by }; break; }
    }
    if (!spot) spot = { x: Math.min(cx + 8, S - w - 2), y: cy - 6 };
    boxes.push({ x: spot.x, y: spot.y, w, h });
    chosen.push(`<g class="tok ${cls}"><circle cx="${cx}" cy="${cy}" r="${u.me || u.enemy_jungler ? 6 : 4}"/>
      <text x="${spot.x}" y="${spot.y + 10}">${esc(text)}</text></g>`);
  }
  const tokens = chosen.reverse().join("");
  const objs = snap.objectives.map((o) => `<text class="obj" x="${X(o.x)}" y="${Y(o.y)}" text-anchor="middle">${esc(o.name)} ${esc(o.text)}</text>`).join("");
  return `<div class="board-wrap"><svg class="board" viewBox="0 0 ${S} ${S}" width="${S}" height="${S}">
    <rect x="0" y="0" width="${S}" height="${S}" rx="12" class="bg"/>
    <path d="M${pad} ${S - pad} L${pad} ${pad} L${S - pad} ${pad}" class="lane ${laneCls(L.top)}"/>
    <path d="M${pad} ${S - pad} L${S - pad} ${pad}" class="lane ${laneCls(L.mid)}"/>
    <path d="M${pad} ${S - pad} L${S - pad} ${S - pad} L${S - pad} ${pad}" class="lane ${laneCls(L.bot)}"/>
    <path d="M${pad + 30} ${pad + 30} L${S - pad - 30} ${S - pad - 30}" class="river"/>
    <text class="base" x="${pad + 4}" y="${S - pad - 6}">우리 본진</text><text class="base" x="${S - pad - 4}" y="${pad + 14}" text-anchor="end">상대 본진</text>
    <text class="lanelbl ${laneCls(L.top)}" x="${pad + 6}" y="${pad + 14}">탑 ${laneSay(L.top)}</text>
    <text class="lanelbl ${laneCls(L.mid)}" x="${S / 2 + 10}" y="${S / 2 - 8}">미드 ${laneSay(L.mid)}</text>
    <text class="lanelbl ${laneCls(L.bot)}" x="${S - pad - 6}" y="${S - pad - 6}" text-anchor="end">봇 ${laneSay(L.bot)}</text>
    <text class="rivlbl" x="${S * 0.68}" y="${S * 0.62}">강</text>
    ${objs}${tokens}</svg>
    <div class="legend board-legend"><span class="lg me">● 나</span><span class="lg ejg">● 상대 정글</span><span class="lg ally">● 우리 팀</span><span class="lg enemy">● 상대 팀</span>
    <span class="muted">${snap.minute}:00 순간 위치 · 라인 색: 초록 우리 유리, 빨강 불리 (라인 골드 차)</span></div></div>`;
}

async function loadMoments(matchId) {
  const box = $("moments-box");
  try {
    const list = await api(`/api/review/${matchId}/moments`);
    if (!list.length) { box.innerHTML = ""; return; }
    box.innerHTML = `<h3 class="sec">그 순간으로 돌아가기 <span class="muted">먼저 직접 골라 보고, 고티어는 비슷한 상황에서 뭘 했는지 확인해요</span></h3>
      ${list.map((mo, i) => `<div class="moment" id="mo-${i}">
        <div class="mo-head"><span class="mo-time">${mo.minute}:00</span> ${esc(mo.reason)}</div>
        <div class="mo-body">${snapshotMap(mo.snapshot)}
          <div class="mo-side"><ul class="mo-facts">${mo.snapshot.facts.map((f) => `<li>${linkify(f)}</li>`).join("")}</ul>
            <div class="mo-q">여기서 뭐 할래요?</div>
            <div class="mo-choices">${mo.choices.map((c) => `<button class="choice" data-a="${c.action}">${esc(c.label)}</button>`).join("")}</div>
            <div class="mo-reveal hidden"></div></div></div></div>`).join("")}`;
    list.forEach((mo, i) => {
      const card = $(`mo-${i}`);
      card.querySelectorAll(".mo-choices .choice").forEach((btn) => (btn.onclick = () => revealMoment(matchId, mo, card, btn.dataset.a)));
    });
  } catch (e) { box.innerHTML = `<p class="muted">${esc(e.message)}</p>`; }
}

function revealMoment(matchId, mo, card, choice) {
  if (card.dataset.done) return;
  card.dataset.done = "1";
  const good = mo.good.includes(choice);
  card.querySelectorAll(".mo-choices .choice").forEach((b) => {
    if (b.dataset.a === choice) b.classList.add(good ? "right" : "wrong");
    if (mo.good.includes(b.dataset.a)) b.classList.add("right");
  });
  const fmtSwing = (v) => (v == null ? "-" : `${v >= 0 ? "+" : ""}${Math.round(v).toLocaleString()}`);
  const bars = mo.crowd.slice(0, 6).map((c) => `<div class="crowd-row ${c.action === mo.mine.action ? "mine" : ""} ${c.action === choice ? "picked" : ""}">
      <span class="cl">${esc(c.label)}</span><span class="cbar"><i style="width:${Math.round(c.share * 100)}%"></i></span>
      <span class="cs">${Math.round(c.share * 100)}%</span>
      <span class="co">팀 골드 ${fmtSwing(c.swing)} · 데스 ${Math.round(c.died * 100)}%</span></div>`).join("");
  const mineOut = `${mo.mine.label} → 2분 뒤 팀 골드 ${fmtSwing(mo.mine.swing)}${mo.mine.died ? " · 내가 죽음" : ""}${mo.mine.obj > 0 ? " · 오브젝트 획득" : mo.mine.obj < 0 ? " · 오브젝트 내줌" : ""}`;
  const rv = card.querySelector(".mo-reveal");
  rv.classList.remove("hidden");
  rv.innerHTML = `<div class="mo-verdict ${good ? "good" : "bad"}">${good ? "좋은 선택이에요" : "고티어는 다르게 많이 골랐어요"} — ${esc(mo.verdict)}</div>
    <div class="mo-mine">실제로 내가 한 것: <b>${esc(mineOut)}</b></div>
    <div class="crowd"><div class="muted">비슷한 상황의 ${esc(mo.pool_label)} 정글러 ${mo.k}명이 다음 1분에 한 것과 2분 뒤 결과</div>${bars}</div>
    ${conceptChipsFor(mo.concepts)}
    <button class="ghost small" onclick="openReplay('${matchId}', ${mo.t})">🎬 리플레이로 이 장면 보기</button>
    <p class="muted">결과는 '그 행동을 한 판들'의 평균이라 상황이 조금씩 달라요. 같은 행동도 실행에 따라 결과가 달라질 수 있어요.</p>`;
  api("/api/moments/answer", { method: "POST", body: JSON.stringify({ match_id: matchId, minute: mo.minute, choice, good,
    concepts: mo.concepts.map((c) => c.id), moment: compactMoment(mo) }) }).catch(() => {});
}

function conceptChipsFor(list) {
  return (list || []).length ? `<div>${list.map((c) => `<button class="chip-link" onclick="openConcept('${c.id}')">📘 ${esc(c.title)}</button>`).join("")}</div>` : "";
}

async function openReplay(matchId, t) {
  openModal(`<h2>리플레이 여는 중…</h2><p class="muted">롤 클라이언트에서 이 경기 리플레이를 받고, ${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")} 조금 앞으로 이동해요. 최대 1~2분 걸릴 수 있어요.</p>`);
  try {
    const r = await api(`/api/replay/${matchId}`, { method: "POST", body: JSON.stringify({ t }) });
    openModal(`<h2>${r.status === "ok" ? "리플레이를 열었어요" : "리플레이를 열지 못했어요"}</h2><p>${esc(r.message || "")}</p>
      ${(r.log || []).length ? `<details class="more"><summary>진행 기록</summary><ul>${r.log.map((l) => `<li class="muted">${esc(l)}</li>`).join("")}</ul></details>` : ""}`);
  } catch (e) { openModal(`<h2>리플레이를 열지 못했어요</h2><p>${esc(e.message)}</p>`); }
}
window.openReplay = openReplay;

function compactMoment(mo) {
  return { match_id: currentMatch, minute: mo.minute, t: mo.t, reason: mo.reason, snapshot: mo.snapshot, choices: mo.choices,
    crowd: mo.crowd.slice(0, 6), good: mo.good, verdict: mo.verdict, mine: mo.mine, k: mo.k, pool_label: mo.pool_label, concepts: mo.concepts };
}

/* ---------- 오늘의 복습 ---------- */
let reviewQueue = [];
async function startReview() {
  await ensureLearn().catch(() => {});
  const r = await api("/api/srs/due");
  reviewQueue = r.items;
  nextReview(0, 0);
}
window.startReview = startReview;

function nextReview(i, right) {
  if (i >= reviewQueue.length) {
    openModal(`<h2>오늘 복습 끝!</h2><p>${reviewQueue.length}개 중 ${right}개를 맞혔어요. 틀린 건 내일 다시, 맞힌 건 간격을 늘려서 다시 나와요.</p>
      <button class="primary" onclick="closeModal();loadHome()">홈으로</button>`);
    return;
  }
  const it = reviewQueue[i];
  const head = `<div class="muted">복습 ${i + 1} / ${reviewQueue.length}</div>`;
  const finish = async (correct, html) => {
    await api("/api/srs/grade", { method: "POST", body: JSON.stringify({ key: it.key, correct }) });
    $("rv-after").innerHTML = html + `<button class="primary" id="rv-next">다음</button>`;
    $("rv-next").onclick = () => nextReview(i + 1, right + (correct ? 1 : 0));
  };
  if (it.kind === "quiz") {
    openModal(`${head}<h2>${esc(it.concept.title)}</h2><div class="quiz"><div class="q">${esc(it.q)}</div>
      ${it.choices.map((c, ci) => `<button class="choice" data-c="${ci}">${esc(c)}</button>`).join("")}</div><div id="rv-after"></div>`);
    document.querySelectorAll(".modal .choice").forEach((b) => (b.onclick = () => {
      const ok = +b.dataset.c === it.answer;
      b.classList.add(ok ? "right" : "wrong");
      document.querySelector(`.modal .choice[data-c="${it.answer}"]`).classList.add("right");
      document.querySelectorAll(".modal .choice").forEach((x) => (x.onclick = null));
      finish(ok, `<p>${esc(it.explain)}</p>`);
    }));
  } else {
    const mo = it.moment;
    openModal(`${head}<h2>${mo.minute}:00 · ${esc(mo.reason)}</h2><div class="mo-body small">${snapshotMap(mo.snapshot, 260)}
      <div><ul class="mo-facts">${mo.snapshot.facts.map((f) => `<li>${linkify(f)}</li>`).join("")}</ul>
      <div class="mo-q">여기서 뭐 할래요?</div><div class="mo-choices">${mo.choices.map((c) => `<button class="choice" data-a="${c.action}">${esc(c.label)}</button>`).join("")}</div></div></div>
      <div id="rv-after"></div>`);
    document.querySelectorAll(".modal .mo-choices .choice").forEach((b) => (b.onclick = () => {
      const ok = mo.good.includes(b.dataset.a);
      document.querySelectorAll(".modal .mo-choices .choice").forEach((x) => {
        if (mo.good.includes(x.dataset.a)) x.classList.add("right");
        x.onclick = null;
      });
      if (!ok) b.classList.add("wrong");
      const bars = mo.crowd.map((c) => `<div class="crowd-row"><span class="cl">${esc(c.label)}</span><span class="cbar"><i style="width:${Math.round(c.share * 100)}%"></i></span><span class="cs">${Math.round(c.share * 100)}%</span></div>`).join("");
      finish(ok, `<div class="mo-verdict ${ok ? "good" : "bad"}">${ok ? "좋아요" : "다시 보기"} — ${esc(mo.verdict)}</div><div class="crowd">${bars}</div>`);
    }));
  }
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
  $("learn-reco").innerHTML = idx.recommended.length ? `<div class="reco"><h4>다시 볼 개념 · 복기에서 지적됨</h4>
      ${idx.recommended.map((r) => `<div class="learn-item" onclick="openConcept('${r.id}')">${esc(r.title)}<span class="lv">${r.count}판</span></div>`).join("")}</div>` : "";
  $("learn-list").innerHTML = idx.categories.map((cat) => {
    const items = idx.concepts.filter((c) => c.category === cat.id && match(c));
    if (!items.length) return "";
    return `<div class="learn-cat">${esc(cat.name)}</div>` + items.map((c) => {
      const qz = idx.quiz[c.id];
      const dot = qz && qz.total && qz.correct / qz.total >= 0.8 ? "done" : idx.read[c.id] ? "read" : "";
      return `<div class="learn-item" data-id="${c.id}" onclick="openConcept('${c.id}')"><span class="dot ${dot}"></span>${esc(c.title)}
        ${c.measurable ? '<span class="lv" title="경기 기록으로 체크 가능">🎯</span>' : `<span class="lv">${esc(LEVEL_KO[c.level] || "")}</span>`}</div>`;
    }).join("");
  }).join("") || `<p class="muted">개념 데이터가 없어요.</p>`;
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
  const mastery = c.mastery && c.mastery.score != null ? `<div class="mastery-line">숙련도 <b>${c.mastery.score}</b> · ${esc(c.mastery.level)} <span class="muted">(경기 체크·판단 훈련·퀴즈 ${c.mastery.n}회 기준)</span></div>` : "";
  const focusBtn = c.is_focus ? '<span class="pill on">지금 연습 중</span>'
    : `<button class="primary" onclick="setFocus('${c.id}').then(() => openConcept('${c.id}'))">이걸 연습 목표로</button>`;
  const goalBox = c.goal
    ? `<div class="goal-box"><div>🎯 <b>경기에서 이렇게 체크해요</b>: ${esc(c.goal)}</div>${hist}${mastery}${focusBtn}</div>`
    : mastery;
  const cat = (learnIndex.categories.find((x) => x.id === c.category) || {}).name || "";
  $("learn-detail").innerHTML = `
    <div class="crumb">${esc(cat)} · ${esc(LEVEL_KO[c.level] || "")}${c.flagged ? ` · 내 복기에서 ${c.flagged}판 지적됨` : ""}</div>
    <h1>${esc(c.title)}<span class="en">${esc(c.en || "")}</span></h1>
    <div class="summary">${esc(c.summary || "")}</div>
    ${c.validation_note ? `<div class="validation-note"><b>📊 실제 경기로 확인한 것</b><p>${esc(c.validation_note)}</p></div>` : ""}
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
async function loadKeyState() {
  try {
    const k = await api("/api/riot-key");
    $("key-state").textContent = k.set && !k.problem ? `· 저장됨 (${k.masked})` : `· ${k.problem || "없음"}`;
  } catch (e) { /* noop */ }
}
document.addEventListener("click", async (ev) => {
  if (ev.target && ev.target.id === "save-key") {
    $("key-state").textContent = "· 확인 중…";
    try {
      const r = await api("/api/riot-key", { method: "PUT", body: JSON.stringify({ key: $("set-key").value }) });
      $("key-state").textContent = `· 저장됨 (${r.masked}) ✓`; $("set-key").value = "";
    } catch (e) { $("key-state").textContent = `· ${e.message}`; }
  }
});

async function loadSettings() {
  loadKeyState();
  await ensureChamps();
  const s = await api("/api/settings");
  $("set-riot-id").value = s.riot_id || "";
  $("set-bucket").value = s.my_bucket || "platinum";
  $("set-target").value = s.target_bucket || "emerald";
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
    await api("/api/settings", { method: "PUT", body: JSON.stringify({ riot_id: $("set-riot-id").value.trim(), my_bucket: $("set-bucket").value, target_bucket: $("set-target").value, ai_enabled: $("set-ai").checked, champion_pool: [...pool] }) });
    $("settings-status").textContent = "저장했어요. 다음 챔피언 선택부터 적용돼요.";
    $("riot-id").value = $("set-riot-id").value.trim();
  } catch (e) { $("settings-status").textContent = e.message; }
};

/* ---------------- 시작 ---------------- */
connect();
loadStatus().then(() => ensureLearn().catch(() => {})).then(() => { loadHome().catch(() => {}); idleFocus(); });
setInterval(loadStatus, 15000);
