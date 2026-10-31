const STAGE_KO = {
  planning: "선픽 의도 표시", banning: "밴 단계", pre_my_pick: "내 픽 전 · 추천",
  post_my_pick: "내 픽 확정 · 조합 브리핑", final: "전원 확정 · 최종 게임 플랜",
};
const $ = (id) => document.getElementById(id);
let ddragon = "";
let evidence = {};
const openCards = new Set(["route", "ganks", "matchup", "objectives", "comp"]);

const icon = (key) => key && ddragon ? `https://ddragon.leagueoflegends.com/cdn/${ddragon}/img/champion/${key}.png` : "";
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function evChips(ids) {
  return (ids || []).map((id) => {
    const e = evidence[id];
    if (!e) return "";
    const tip = `${e.text}\n— ${e.source}${e.confidence ? ` · 신뢰도 ${e.confidence}` : ""}`;
    const cls = e.confidence === "낮음" ? "low" : e.confidence === "높음" ? "high" : "";
    return `<span class="ev ${cls}" data-tip="${esc(tip)}">${id}${e.games != null ? ` n=${e.games}` : ""}</span>`;
  }).join("");
}

function renderTeams(st) {
  const row = (x) => `<li class="${x.me ? "me" : ""} ${x.picking ? "picking" : ""}">
      <span class="pos">${esc(x.position)}</span>
      ${x.key ? `<img src="${icon(x.key)}" alt="">` : `<img alt="">`}
      <span class="${x.hovering ? "hover" : ""}">${esc(x.name || "—")}${x.me ? " (나)" : ""}</span></li>`;
  $("allies").innerHTML = st.allies.map(row).join("");
  $("enemies").innerHTML = st.enemies.map(row).join("");
  const bans = (list) => list.map((b) => b.key ? `<img src="${icon(b.key)}" title="${esc(b.key)}">` : "").join("");
  $("ally-bans").innerHTML = bans(st.ally_bans);
  $("enemy-bans").innerHTML = bans(st.enemy_bans);
}

function renderRecs(b, keyOf) {
  const show = b.picks.length || b.bans.length;
  $("recs").classList.toggle("hidden", !show);
  const rec = (r, isBan) => `<li class="rec"><div class="rec-top">
      <img src="${icon(keyOf[r.champion_id])}" alt=""><span class="rec-name">${esc(r.name)}</span>
      ${isBan ? "" : `<span class="rec-score">예상 ${(r.score * 100).toFixed(1)}%</span>`}</div>
      <ul>${r.reasons.map((i) => `<li>${esc(i.text)}${evChips(i.evidence)}</li>`).join("")}</ul></li>`;
  $("picks").innerHTML = b.picks.map((r) => rec(r, false)).join("") || `<li class="muted">-</li>`;
  $("bans").innerHTML = b.bans.map((r) => rec(r, true)).join("") || `<li class="muted">밴 단계가 지났습니다</li>`;
}

function renderCards(b) {
  const box = $("cards");
  box.innerHTML = "";
  for (const c of b.cards) {
    const el = $("tpl-card").content.firstElementChild.cloneNode(true);
    el.querySelector(".card-title").textContent = c.title;
    el.querySelector(".card-headline").textContent = c.headline;
    el.querySelector(".card-items").innerHTML = c.items
      .map((i) => `<li class="${i.kind}">${esc(i.text)}${evChips(i.evidence)}</li>`).join("");
    if (openCards.has(c.id)) el.classList.add("open");
    el.querySelector(".card-head").onclick = () => {
      el.classList.toggle("open");
      el.classList.contains("open") ? openCards.add(c.id) : openCards.delete(c.id);
    };
    box.appendChild(el);
  }
}

function renderAI(msg) {
  const box = $("ai");
  box.classList.remove("hidden");
  $("ai-status").textContent = "";
  if (msg.status === "running") {
    $("ai-headline").textContent = "근거를 바탕으로 운영 방향 정리 중…";
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
  $("ai-points").innerHTML = msg.points
    .map((p) => `<li><span class="phase">${esc(p.phase)}</span>${esc(p.text)}${evChips(p.evidence)}</li>`).join("");
  if (msg.dropped) $("ai-status").textContent = `근거 없는 문장 ${msg.dropped}개는 표시하지 않았습니다.`;
}

function onBriefing(msg) {
  ddragon = msg.ddragon || ddragon;
  const st = msg.state, b = msg.briefing;
  evidence = Object.fromEntries(b.evidence.map((e) => [e.id, e]));
  const keyOf = {};
  for (const x of [...st.allies, ...st.enemies]) keyOf[x.champion_id] = x.key;
  for (const r of [...b.picks, ...b.bans]) keyOf[r.champion_id] ??= r.key;
  $("idle").classList.add("hidden");
  $("stage").textContent = `${STAGE_KO[b.stage] || b.stage}${b.my_champion_name ? ` · ${b.my_champion_name}` : ""}` +
    (b.enemy_jungler_name ? ` vs ${b.enemy_jungler_name}` : "");
  $("scope").textContent = b.scope_label ? `데이터: ${b.scope_label}` : "";
  $("notes").innerHTML = b.notes.map((n) => `<div class="note">${esc(n)}</div>`).join("");
  renderTeams(st);
  renderRecs(b, keyOf);
  renderCards(b);
  if (!["post_my_pick", "final"].includes(b.stage)) $("ai").classList.add("hidden");
}

function onIdle() {
  $("idle").classList.remove("hidden");
  $("stage").textContent = "대기 중";
  for (const id of ["recs", "ai"]) $(id).classList.add("hidden");
  $("cards").innerHTML = ""; $("notes").innerHTML = "";
}

async function loadStatus() {
  try {
    const s = await (await fetch("/api/status")).json();
    ddragon = s.ddragon || ddragon;
    const parts = [s.lcu ? "롤 클라이언트 연결됨" : "롤 클라이언트 미실행"];
    parts.push(s.stats && s.stats.built_at ? `통계 갱신 ${s.stats.built_at.replace("T", " ").slice(0, 16)}` : "통계 없음 (loldosa update)");
    parts.push(s.ai && s.ai.enabled ? `AI: Claude ${s.ai.model}` : "AI 꺼짐");
    $("status-line").textContent = parts.join(" · ");
  } catch (e) { /* 서버 재시작 중 */ }
}

function connect() {
  const ws = new WebSocket(`ws://${location.host}/ws`);
  ws.onopen = () => { $("conn").textContent = "● 연결됨"; $("conn").className = "conn on"; loadStatus(); };
  ws.onclose = () => { $("conn").textContent = "● 끊김 — 재연결 중"; $("conn").className = "conn off"; setTimeout(connect, 1500); };
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.type === "briefing") onBriefing(msg);
    else if (msg.type === "ai") renderAI(msg);
    else if (msg.type === "idle") onIdle();
  };
}
connect();
setInterval(loadStatus, 15000);
