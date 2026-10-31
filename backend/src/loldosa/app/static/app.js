const STAGE_KO = {
  planning: "선픽 의도 표시", banning: "밴 단계", pre_my_pick: "내 픽 전",
  post_my_pick: "내 픽 확정", final: "전원 확정",
};
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
let ddragon = "";
let evidence = {};
const openCards = new Set();
const icon = (key) => (key && ddragon ? `https://ddragon.leagueoflegends.com/cdn/${ddragon}/img/champion/${key}.png` : "");
const imgTag = (key, cls = "") => `<img class="${cls}" src="${icon(key)}" alt="" onerror="this.style.visibility='hidden'">`;

/* ---------------- 공통: 탭, 근거 토글 ---------------- */
document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("active", x === b));
  document.querySelectorAll(".tabpane").forEach((p) => p.classList.toggle("active", p.id === `tab-${b.dataset.tab}`));
  if (b.dataset.tab === "review") loadMatches();
  if (b.dataset.tab === "settings") loadSettings();
  if (b.dataset.tab === "learn") loadLearn();
}));
function switchTab(name) { document.querySelector(`.tab[data-tab=${name}]`).click(); }
const showEv = $("show-ev");
showEv.checked = localStorage.getItem("showEv") === "1";
document.body.classList.toggle("show-ev", showEv.checked);
showEv.onchange = () => { localStorage.setItem("showEv", showEv.checked ? "1" : "0"); document.body.classList.toggle("show-ev", showEv.checked); };

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

/* ---------------- 브리핑 ---------------- */
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

function renderPicks(b) {
  const show = b.picks.length || b.bans.length;
  $("picks-box").classList.toggle("hidden", !show);
  $("picks").innerHTML = b.picks.map((r) => pickCard(r)).join("") || `<span class="muted">추천할 후보가 없습니다</span>`;
  $("picks-outside-wrap").classList.toggle("hidden", !b.picks_outside.length);
  $("picks-outside").innerHTML = b.picks_outside.map((r) => pickCard(r)).join("");
  $("bans-wrap").classList.toggle("hidden", !b.bans.length);
  $("bans").innerHTML = b.bans.map((r) => pickCard(r, { score: false })).join("");
  $("pool-hint").textContent = b.picks.some((r) => r.in_pool) ? "내 챔프폭 안에서 추천 · 카드를 누르면 이유" :
    "설정에서 챔프폭을 고르면 그 안에서 추천해요 · 카드를 누르면 이유";
}

function renderPlan(b) {
  $("plan-box").classList.toggle("hidden", !b.plan.length);
  $("plan").innerHTML = b.plan.map((p) => `<li><span class="tag ${p.title === "주의" ? "warn" : ""}">${esc(p.title)}</span>
      <span class="txt">${esc(p.text)}${evChips(p.evidence)}${conceptChips(p.concepts)}</span></li>`).join("");
}

function renderCards(b) {
  const box = $("cards");
  box.innerHTML = "";
  for (const c of b.cards) {
    const el = document.createElement("article");
    el.className = `card ${openCards.has(c.id) ? "open" : ""}`;
    el.innerHTML = `<button class="card-head"><span class="card-title">${esc(c.title)}</span>
        <span class="card-headline">${esc(c.headline)}</span><span class="chev">▾</span></button>
      <ul class="card-items">${c.items.map((i) => `<li class="${i.kind}">${esc(i.text)}${evChips(i.evidence)}</li>`).join("")}</ul>`;
    el.querySelector(".card-head").onclick = () => {
      el.classList.toggle("open");
      el.classList.contains("open") ? openCards.add(c.id) : openCards.delete(c.id);
    };
    box.appendChild(el);
  }
}
$("expand-all").onclick = () => {
  const all = [...document.querySelectorAll("#cards .card")];
  const open = all.some((c) => !c.classList.contains("open"));
  all.forEach((c) => c.classList.toggle("open", open));
  $("expand-all").textContent = open ? "모두 접기" : "모두 펼치기";
};

function renderAI(msg) {
  $("ai").classList.remove("hidden");
  $("ai-status").textContent = "";
  if (msg.status === "running") {
    $("ai-headline").textContent = "근거를 바탕으로 정리 중… (10~20초)";
    $("ai-points").innerHTML = "";
    return;
  }
  if (msg.status !== "ok") {
    $("ai-headline").textContent = "AI 코치를 사용할 수 없습니다";
    $("ai-points").innerHTML = "";
    $("ai-status").textContent = msg.message || "";
    return;
  }
  $("ai-headline").textContent = msg.headline;
  $("ai-points").innerHTML = msg.points.map((p) => `<li><span class="phase">${esc(p.phase)}</span>${esc(p.text)}${evChips(p.evidence)}</li>`).join("");
  if (msg.dropped) $("ai-status").textContent = `근거 없는 문장 ${msg.dropped}개는 표시하지 않았습니다.`;
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
  $("notes").innerHTML = b.notes.map((n) => `<div class="note">${esc(n)}</div>`).join("");
  renderTeams(st);
  renderPicks(b);
  renderPlan(b);
  renderCards(b);
  if (!["post_my_pick", "final"].includes(b.stage)) $("ai").classList.add("hidden");
}

/* ---------------- 상태 ---------------- */
async function loadStatus() {
  try {
    const s = await (await fetch("/api/status")).json();
    ddragon = s.ddragon || ddragon;
    $("pill-lcu").textContent = s.replay ? "데모 재생" : s.lcu ? "클라이언트 연결" : "클라이언트 꺼짐";
    $("pill-lcu").className = `pill ${s.lcu ? "on" : "off"}`;
    $("pill-ai").textContent = s.ai && s.ai.enabled ? `AI ${s.ai.model}` : "AI 꺼짐";
    $("pill-ai").className = `pill ${s.ai && s.ai.enabled ? "on" : ""}`;
    const built = s.stats && s.stats.built_at ? `통계 갱신 ${s.stats.built_at.replace("T", " ").slice(0, 16)}` : "통계 없음 → loldosa update";
    $("status-line").textContent = built;
  } catch (e) { /* 재시작 중 */ }
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

/* ---------------- 경기 리뷰 ---------------- */
let currentMatch = null;

async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || `오류 ${r.status}`);
  return data;
}

function renderMatchList(list) {
  $("match-list").innerHTML = list.map((m) => `<li class="match ${m.win ? "win" : "loss"} ${m.match_id === currentMatch ? "active" : ""}" data-id="${m.match_id}">
      ${imgTag(champKey(m.champion_id))}
      <div><div class="m1">${esc(champName(m.champion_id))} <span class="muted">${esc(posKo(m.position))}</span></div>
      <div class="m2">${m.kills}/${m.deaths}/${m.assists} · ${String(m.game_start).slice(5, 16).replace("T", " ")}${m.enemy_jungler ? ` · vs ${esc(champName(m.enemy_jungler))}` : ""}</div></div>
      <span class="res">${m.win ? "승" : "패"}</span></li>`).join("") || `<li class="muted" style="padding:12px">불러온 경기가 없어요. 위에 Riot ID를 넣고 '경기 불러오기'를 누르세요.</li>`;
  document.querySelectorAll(".match").forEach((li) => (li.onclick = () => openReview(li.dataset.id)));
}

const POS = { TOP: "탑", JUNGLE: "정글", MIDDLE: "미드", BOTTOM: "원딜", UTILITY: "서폿" };
const posKo = (p) => POS[p] || p || "";
let champMap = {};
const champName = (id) => (champMap[id] ? champMap[id].name : `#${id}`);
const champKey = (id) => (champMap[id] ? champMap[id].key : "");
async function ensureChamps() {
  if (Object.keys(champMap).length) return;
  const list = await api("/api/champions");
  champMap = Object.fromEntries(list.map((c) => [c.id, c]));
  window._champList = list;
}

async function loadMatches() {
  await ensureChamps();
  const s = await api("/api/settings");
  if (!$("riot-id").value) $("riot-id").value = s.riot_id || "";
  renderMatchList(await api("/api/review/matches"));
}

$("review-sync").onclick = async () => {
  const btn = $("review-sync");
  btn.disabled = true;
  $("review-status").textContent = "Riot 서버에서 경기 받는 중… (경기당 1~2초)";
  try {
    await ensureChamps();
    const list = await api("/api/review/sync", { method: "POST", body: JSON.stringify({ riot_id: $("riot-id").value, count: +$("review-count").value }) });
    renderMatchList(list);
    $("review-status").textContent = `${list.length}경기`;
    if (list.length && !currentMatch) openReview(list[0].match_id);
  } catch (e) {
    $("review-status").textContent = e.message;
  } finally { btn.disabled = false; }
};

function minimap(rv) {
  const S = 360, M = 14870;
  const px = (x) => (x / M) * S, py = (y) => S - (y / M) * S;
  const path = (pts, color) => pts.length ? `<polyline points="${pts.map((p) => `${px(p[1])},${py(p[2])}`).join(" ")}" fill="none"
      stroke="${color}" stroke-width="2" stroke-opacity=".75"/>` + pts.map((p) => `<circle cx="${px(p[1])}" cy="${py(p[2])}" r="${p[0] <= 4 ? 7 : 5}"
      fill="${color}" fill-opacity=".85"/><text x="${px(p[1])}" y="${py(p[2]) + 3}" font-size="8" text-anchor="middle" fill="#000">${p[0]}</text>`).join("") : "";
  const marks = rv.moments.filter((m) => m.x != null && m.t <= 660 && ["death", "enemy_gank", "objective"].includes(m.kind)).map((m) => {
    const c = m.kind === "objective" ? (m.good ? "#3ccf91" : "#ffb547") : "#ff5f66";
    const sym = m.kind === "objective" ? "◆" : "✕";
    return `<text x="${px(m.x)}" y="${py(m.y) + 5}" font-size="14" text-anchor="middle" fill="${c}"><title>${esc(m.text)}</title>${sym}</text>`;
  }).join("");
  return `<div class="minimap"><img src="https://ddragon.leagueoflegends.com/cdn/${ddragon}/img/map/map11.png" alt="" onerror="this.remove()">
    <svg viewBox="0 0 ${S} ${S}">${path(rv.paths.enemy_jungler, "#ff5f66")}${path(rv.paths.me, "#f0d79a")}${marks}</svg></div>
    <div class="legend"><span><i style="background:#f0d79a"></i>나 (숫자=분)</span><span><i style="background:#ff5f66"></i>적 정글</span>
    <span style="color:#ff5f66">✕ 데스/적 갱</span><span style="color:#ffb547">◆ 적 오브젝트</span><span style="color:#3ccf91">◆ 우리 오브젝트</span></div>`;
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
    const lessons = rv.lessons.slice(0, 5).map((l) => `<div class="lesson sev${Math.min(l.severity, 3)}"><h4>${esc(l.title)}</h4>
        <p>${esc(l.text)}${evChips(l.evidence, pool)}</p>${conceptChips(l.concepts)}</div>`).join("");
    const strengths = rv.strengths.map((l) => `<span class="strength">✓ ${esc(l.title)}</span>`).join("");
    const metrics = rv.metrics.map((m) => `<tr><td>${esc(m.label)}</td><td class="${m.verdict}">${esc(m.mine)}</td><td>${esc(m.bench)}</td>
        <td>${evChips(m.evidence, pool)}</td></tr>`).join("");
    const moments = rv.moments.map((m) => `<li class="${m.good === true ? "good" : m.good === false ? "bad" : ""}">${esc(m.text)}</li>`).join("");
    box.innerHTML = `
      <div class="rv-head">${imgTag(sm.key)}<div>
        <h2>${esc(sm.champion)} <span class="${sm.win ? "res-win" : "res-loss"}">${sm.win ? "승리" : "패배"}</span></h2>
        <div class="muted">${esc(sm.position)} · ${esc(sm.side)} · ${esc(sm.kda)} · ${esc(sm.duration)} · ${esc(sm.date)}${sm.enemy_jungler ? ` · 상대 정글 ${esc(sm.enemy_jungler)}` : ""}</div></div></div>
      ${rv.notes.map((n) => `<div class="note" style="margin-bottom:10px">${esc(n)}</div>`).join("")}
      <div class="rv-grid"><div>
        <h3 class="sec">이렇게 했어야 해요</h3>${lessons || `<p class="muted">눈에 띄는 문제가 없어요.</p>`}
        ${strengths ? `<h3 class="sec">잘한 점</h3><div class="strengths">${strengths}</div>` : ""}
        <div id="rv-ai"><button class="primary" id="rv-ai-btn">AI 복기 코칭 받기</button></div>
        ${metrics ? `<h3 class="sec">고티어와 비교 <span class="muted">${esc(rv.scope_label)}</span></h3>
          <table class="metrics"><tr><th>항목</th><th>나</th><th>고티어</th><th></th></tr>${metrics}</table>` : ""}
      </div><div>
        <h3 class="sec">10분까지 동선</h3>${minimap(rv)}
        <h3 class="sec">주요 순간</h3><ul class="moments">${moments}</ul>
      </div></div>`;
    $("rv-ai-btn").onclick = async () => {
      const btn = $("rv-ai-btn");
      btn.disabled = true; btn.textContent = "정리 중… (10~20초)";
      try {
        const r = await api(`/api/review/${id}/ai`, { method: "POST" });
        $("rv-ai").innerHTML = r.status === "ok" ? `<div class="ai"><div class="ai-head"><span class="badge">AI 복기</span>${esc(r.headline)}</div>
          <ol>${r.points.map((p) => `<li><span class="phase">${esc(p.phase)}</span>${esc(p.text)}${evChips(p.evidence, pool)}</li>`).join("")}</ol></div>`
          : `<p class="muted">${esc(r.message || "AI 코치를 사용할 수 없습니다")}</p>`;
      } catch (e) { $("rv-ai").innerHTML = `<p class="muted">${esc(e.message)}</p>`; }
    };
  } catch (e) {
    box.innerHTML = `<p class="muted">${esc(e.message)}</p>`;
  }
}

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
  $("champ-grid").innerHTML = list.map((c) => `<div class="champ ${pool.has(c.id) ? "sel" : ""}" data-id="${c.id}" title="${c.jungle_games ? `고티어 정글 ${c.jungle_games}판` : ""}">
      ${imgTag(c.key)}${esc(c.name)}</div>`).join("");
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
    await api("/api/settings", { method: "PUT", body: JSON.stringify({
      riot_id: $("set-riot-id").value.trim(), my_bucket: $("set-bucket").value,
      ai_enabled: $("set-ai").checked, champion_pool: [...pool] }) });
    $("settings-status").textContent = "저장했어요. 다음 챔피언 선택부터 적용됩니다.";
    $("riot-id").value = $("set-riot-id").value.trim();
    loadStatus();
  } catch (e) { $("settings-status").textContent = e.message; }
};

/* ---------------- 개념 학습 ---------------- */
let learnIndex = null;
let conceptTitles = {};
const LEVEL_KO = { basic: "기초", intermediate: "중급", advanced: "심화" };

function conceptChips(list) {
  if (!list || !list.length) return "";
  return `<div>${list.map((c) => {
    const id = typeof c === "string" ? c : c.id;
    const title = typeof c === "string" ? (conceptTitles[c] || c) : c.title;
    return `<button class="chip-link" onclick="openConcept('${esc(id)}')">📘 ${esc(title)}</button>`;
  }).join("")}</div>`;
}

async function ensureLearn() {
  if (learnIndex) return learnIndex;
  learnIndex = await api("/api/learn");
  conceptTitles = Object.fromEntries(learnIndex.concepts.map((c) => [c.id, c.title]));
  return learnIndex;
}

async function loadLearn(refresh = true) {
  if (refresh) learnIndex = null;
  const idx = await ensureLearn();
  const q = $("learn-search").value.trim().replace(/\s/g, "").toLowerCase();
  const match = (c) => !q || [c.title, c.en, c.summary, c.id].join(" ").replace(/\s/g, "").toLowerCase().includes(q);
  $("learn-reco").innerHTML = idx.recommended.length ? `<div class="reco"><h4>추천 학습 · 최근 리뷰에서 지적됨</h4>
      ${idx.recommended.map((r) => `<div class="learn-item" onclick="openConcept('${esc(r.id)}')">${esc(r.title)}<span class="lv">${r.count}경기</span></div>`).join("")}</div>` : "";
  $("learn-list").innerHTML = idx.categories.map((cat) => {
    const items = idx.concepts.filter((c) => c.category === cat.id && match(c));
    if (!items.length) return "";
    return `<div class="learn-cat">${esc(cat.name)}</div>` + items.map((c) => {
      const qz = idx.quiz[c.id];
      const dot = qz && qz.total && qz.correct / qz.total >= 0.8 ? "done" : idx.read[c.id] ? "read" : "";
      return `<div class="learn-item" data-id="${esc(c.id)}" onclick="openConcept('${esc(c.id)}')"><span class="dot ${dot}"></span>${esc(c.title)}
        <span class="lv">${esc(LEVEL_KO[c.level] || c.level || "")}</span></div>`;
    }).join("");
  }).join("") || `<p class="muted">개념 데이터가 없습니다.</p>`;
}
$("learn-search").oninput = () => loadLearn(false);

function listBlock(title, arr, ordered = false) {
  if (!arr || !arr.length) return "";
  const tag = ordered ? "ol" : "ul";
  return `<h3>${title}</h3><${tag}>${arr.map((x) => `<li>${esc(x)}</li>`).join("")}</${tag}>`;
}

async function openConcept(id) {
  if (!document.getElementById("tab-learn").classList.contains("active")) switchTab("learn");
  await ensureLearn();
  const c = await api(`/api/learn/${encodeURIComponent(id)}`);
  document.querySelectorAll("#learn-list .learn-item").forEach((el) => el.classList.toggle("active", el.dataset.id === id));
  const nums = (c.numbers || []).length ? `<h3>수치 (현재 시즌)</h3><table class="numbers">${c.numbers.map((n) =>
      `<tr><td>${esc(n.label)}</td><td>${esc(n.value)}</td><td class="note">${esc(n.note || "")}</td></tr>`).join("")}</table>` : "";
  const quiz = (c.quiz || []).map((q, qi) => `<div class="quiz" data-q="${qi}"><div class="q">Q${qi + 1}. ${esc(q.q)}</div>
      ${q.choices.map((ch, ci) => `<button class="choice" data-c="${ci}">${esc(ch)}</button>`).join("")}
      <div class="explain hidden">${esc(q.explain || "")}</div></div>`).join("");
  $("learn-detail").innerHTML = `
    <h1>${esc(c.title)}<span class="en">${esc(c.en || "")}</span></h1>
    <div class="muted">${esc(LEVEL_KO[c.level] || c.level || "")}${c.flagged ? ` · 내 리뷰에서 ${c.flagged}경기 지적됨` : ""}</div>
    <div class="summary">${esc(c.summary || "")}</div>
    ${c.definition ? `<h3>정의</h3><p>${esc(c.definition)}</p>` : ""}
    ${c.why ? `<h3>왜 중요한가</h3><p>${esc(c.why)}</p>` : ""}
    ${listBlock("어떻게 하나", c.how, true)}
    ${listBlock("정글러 관점", c.jungler)}
    ${listBlock("흔한 실수", c.mistakes)}
    ${nums}
    ${quiz ? `<h3>확인 퀴즈</h3>${quiz}` : ""}
    ${(c.related || []).length ? `<h3>관련 개념</h3>${conceptChips(c.related)}` : ""}
    ${(c.sources || []).length ? `<h3>출처</h3><ul class="sources">${c.sources.map((s) =>
        `<li>${s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title || s.url)}</a>` : esc(s.title)}${s.note ? ` <span class="muted">(${esc(s.note)})</span>` : ""}</li>`).join("")}</ul>` : ""}`;
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
      learnIndex = null;
    }));
  });
  $("learn-detail").scrollTop = 0;
  window.scrollTo(0, 0);
}
window.openConcept = openConcept;

connect();
loadStatus();
ensureLearn().catch(() => {});
setInterval(loadStatus, 15000);
