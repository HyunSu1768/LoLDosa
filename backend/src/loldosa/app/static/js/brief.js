/* 게임 전 브리핑: 밴픽 30초 안에 "그래서 뭐 해?"에 답한다.
 * B1 맨 위엔 결론 한 문장 + 행동 하나 · B2 근거는 3줄, 나머지는 펼쳐서 · B4 스켈레톤·이전 결과 유지
 * B5 내 챔프폭 안에서만 추천(폭 밖은 펼쳐야 보임) · B6 경고는 하나만 · B7 시간은 게임 시계 형식 */
import { $, $$, api, champImg, empty, esc, evChips, linkify, mmss, openSheet, row, state } from "./core.js";

const STAGE = { planning: "픽 미리 찍는 중", banning: "밴하는 중", pre_my_pick: "내 픽 차례 전", post_my_pick: "내 픽 확정", final: "모두 확정" };
const brief = { msg: null, ai: null, ended: false };
let viewEl = null;

export function onBriefingMessage(msg) {
  if (msg.type === "briefing") { brief.msg = msg; brief.ended = false; state.ddragon = msg.ddragon || state.ddragon; }
  if (msg.type === "ai") brief.ai = msg;
  if (msg.type === "ended") brief.ended = true;
  document.dispatchEvent(new CustomEvent("brief-live", { detail: !!brief.msg }));
  if (viewEl && location.hash.startsWith("#/brief")) draw();
}
export const hasLiveBriefing = () => !!brief.msg && !brief.ended;

export async function renderBrief(view) {
  viewEl = view;
  if (!brief.msg) {
    // 챔선 전: 이번 판 연습 하나만 (빈 화면 대신 지금 할 수 있는 일)
    const h = state.home || (await api("/api/home").catch(() => null));
    if (brief.msg) { draw(); return; }  // 기다리는 사이 챔선 메시지가 왔으면 대기 화면으로 덮지 않는다
    const p = h?.practice;
    view.innerHTML = `<div class="page">
      <div class="top"><h1>챔피언 선택을 기다리고 있어요</h1><p>롤에서 큐를 잡으면 이 화면이 자동으로 바뀌어요.</p></div>
      ${p ? `<section class="card suggest"><div class="eyebrow">다음 판에 할 것 하나</div>
        <div class="title" style="font-size:var(--t3);line-height:var(--t3-lh)">${esc(p.label)}</div>
        <div class="body" style="margin-top:8px">지금 <b class="num">${esc(p.mine_text)}</b>, 챌린저는 <b class="num accent">${esc(p.target_text)}</b>예요</div>
        <div class="body" style="margin-top:12px;color:var(--grey900)">다짐: 만약 ${esc(p.if_then || p.drill)}</div></section>`
        : empty({ em: "⏳", title: "큐를 잡으면 바로 보여 드릴게요", desc: "챔피언 선택 화면에서 이번 판 플랜을 정리해 드려요." })}
    </div>`;
    return;
  }
  draw();
}

function teamList(list, mine) {
  return list.map((x) => `<li class="tm ${x.me ? "me" : ""} ${x.picking ? "picking" : ""}">
    <span class="tm-pos">${esc(x.position || "")}</span>
    <span class="tm-img">${x.key ? champImg(x.key, x.name) : ""}</span>
    <span class="tm-name ${x.hovering ? "hover" : ""}">${esc(x.name || "고르는 중")}${x.me ? " · 나" : ""}</span></li>`).join("");
}

function pickRow(r, my) {
  const mine = my[r.champion_id];
  return row({ lead: champImg(r.key, r.name) || "?", title: `${esc(r.name)} ${r.in_pool ? '<span class="badge blue">내 폭</span>' : ""}`,
    sub: esc((r.reasons[1] || r.reasons[0] || {}).text || ""),
    end: mine ? `<div class="val num">${mine.progress}점</div><div class="sub">내 진행도</div>` : "" });
}

function draw() {
  const { msg, ai } = brief;
  const b = msg.briefing, st = msg.state;
  const my = msg.my_champs || {};
  const pool = Object.fromEntries(b.evidence.map((e) => [e.id, e]));
  const picked = ["post_my_pick", "final"].includes(b.stage);
  const plan = b.plan || [];
  const warn = plan.find((p) => p.title === "주의");
  const main = plan.filter((p) => p !== warn);
  const head = main[0];
  const practice = msg.practice || state.home?.practice;
  // 다짐 하나: 연습 목표(채점됨)가 있으면 그 목표, 없으면 챌린저 차이 1위 — 같은 문장이 게임 뒤 채점 기준이 된다
  const fc = msg.focus && msg.focus.graded !== false && msg.focus.if_then ? msg.focus : null;
  const pledge = fc ? { text: fc.if_then, from: `연습 목표 ${fc.title}` }
    : practice ? { text: practice.if_then || practice.drill, from: `챌린저와 가장 큰 차이 ${practice.label}` } : null;
  const pickTop = b.picks[0];

  const heroPicked = head ? `<section class="hero" aria-live="polite">
      <div class="eyebrow">이번 판 플랜 · ${esc(head.title)}</div>
      <div class="brief-hero">${linkify(head.text)}${evChips(head.evidence, pool)}</div></section>
    <div class="list">${main.slice(1, 4).map((p) => row({ lead: `<span class="tag">${esc(p.title)}</span>`, title: linkify(p.text) + evChips(p.evidence, pool) })).join("")}</div>
    ${warn ? `<div class="warn-row" role="alert"><b>주의</b> ${linkify(warn.text)}</div>` : ""}`
    : `<div class="sk big"></div><div class="sk card"></div>`;

  const heroPick = pickTop ? `<section class="hero">
      <div class="eyebrow">${b.stage === "banning" ? "밴할 동안 미리 정해 둘 픽" : "이번 판 추천 픽"}</div>
      <div class="pick-hero">${champImg(pickTop.key, pickTop.name)}<div>
        <div class="brief-hero">${esc(josa2(pickTop.name))} 추천해요</div>
        <div class="body">${esc((pickTop.reasons[1] || pickTop.reasons[0] || {}).text || "")}</div></div></div></section>
    ${b.picks.length > 1 ? `<div class="list">${b.picks.slice(1, 3).map((r) => pickRow(r, my)).join("")}</div>` : ""}
    ${b.bans.length ? `<div class="sub" style="margin-top:16px">밴 추천: ${b.bans.slice(0, 3).map((r) => esc(r.name)).join(", ")}</div>` : ""}`
    : `<p class="body">추천할 챔피언이 없어요. 설정에서 챔프폭을 고르면 그 안에서 추천해 드려요.</p>`;

  viewEl.innerHTML = `<div class="page wide brief-grid">
    <aside class="teams" aria-label="양 팀">
      <div class="side ${st.side}">${st.side === "blue" ? "블루 진영" : "레드 진영"}</div>
      <ul class="tm-list">${teamList(st.allies)}</ul>
      <div class="sub" style="margin:16px 0 8px">상대</div>
      <ul class="tm-list">${teamList(st.enemies)}</ul>
    </aside>
    <div class="brief-main">
      <div class="eyebrow">${esc(STAGE[b.stage] || b.stage)}${brief.ended ? " · 챔피언 선택 끝 (로딩 중에도 볼 수 있어요)" : ""}</div>
      <h1 class="brief-title">${b.my_champion_name ? `${esc(b.my_champion_name)}${b.enemy_jungler_name ? ` <span class="vs">vs</span> ${esc(b.enemy_jungler_name)}` : ""}` : "챔피언을 고르는 중이에요"}</h1>
      ${picked ? heroPicked : heroPick}
      ${pledge ? `<div class="practice-row"><span class="badge yellow">이번 판 다짐</span> <span>만약 ${esc(pledge.text)}</span></div>
        <p class="sub" style="margin-top:6px">게임이 끝나면 이 다짐을 지켰는지 채점해요 · ${esc(pledge.from)}</p>` : ""}
      ${picked ? gamePlan(b.game_plan, pool) : ""}
      <div class="btn-row">
        <button class="btn weak" id="more">근거와 세부 보기</button>
        ${picked && ai ? `<button class="btn grey" id="ai">${ai.status === "running" ? "AI 코치가 정리하는 중…" : ai.status === "ok" ? "AI 코치 정리 보기" : "AI 코치를 쓸 수 없어요"}</button>` : ""}
      </div>
      <p class="sub" style="margin-top:24px">${esc(b.scope_label ? `데이터: ${b.scope_label}` : "")}</p>
    </div></div>`;

  $("#more", viewEl).onclick = () => detailSheet(b, pool, my);
  $$("[data-ph]", viewEl).forEach((r) => (r.onclick = () => phaseSheet(b.game_plan, +r.dataset.ph, pool)));
  $("#ai", viewEl)?.addEventListener("click", () => aiSheet(ai, pool));
}

/* 전체 운영: 지금 할 일(히어로) 아래에 게임 전체 흐름을 시간 순 4줄로. 세부는 눌러서 (B2) */
function gamePlan(gp, pool) {
  if (!gp || !gp.phases || !gp.phases.length) return "";
  return `<h2 class="section">전체 운영<small>우리 ${esc(gp.us.label)}${gp.them ? ` · 상대 ${esc(gp.them.label)}` : ""}</small></h2>
    <div class="list">${gp.phases.map((p, i) => row({ lead: `<span class="tag num">${esc(p.time)}</span>`, title: linkify(p.headline),
      sub: p.why ? `<span class="why-short">왜? ${esc(p.why)}</span>` : esc(p.title), attrs: `data-ph="${i}"` })).join("")}</div>
    ${gp.vs ? `<p class="sub" style="margin-top:8px">${linkify(gp.vs)}</p>` : ""}`;
}
function phaseSheet(gp, i, pool) {
  const p = gp.phases[i];
  openSheet(`<div class="eyebrow num">${esc(p.time)}</div><h2>${esc(p.title)}에 할 일</h2>
    <div class="todo">${p.items.map((x) => x.kind === "rule"
      ? `<p class="sub" style="margin:12px 0 0"><span class="badge blue">2026 규칙</span> ${linkify(x.text)}${evChips(x.evidence, pool)}</p>`
      : `<div class="todo-item"><div class="todo-do">${linkify(x.text)}</div>${x.why ? `<div class="todo-why"><b>왜?</b> ${linkify(x.why)}${evChips(x.evidence, pool)}</div>` : ""}</div>`).join("")}</div>
    <p class="sub" style="margin-top:12px">'2026 규칙'은 실제 경기 시각으로 확인한 사실이고, 나머지는 조합과 코칭 자료로 정리한 판단이에요.</p>
    <div class="card" style="margin-top:12px;background:var(--bg-layer)"><div class="eyebrow">조합을 이렇게 봤어요</div>
      <p class="body" style="margin:4px 0 0">우리: ${esc(gp.us.label)} — ${esc(gp.us.why)}${gp.them ? `<br>상대: ${esc(gp.them.label)} — ${esc(gp.them.why)}` : ""}</p></div>
    <div class="btn-row end">${i > 0 ? `<button class="btn grey m" id="ph-prev">이전 시간대</button>` : ""}${i < gp.phases.length - 1 ? `<button class="btn fill m" id="ph-next">다음 시간대</button>` : `<button class="btn fill m" data-close>닫기</button>`}</div>`);
  $("#ph-prev")?.addEventListener("click", () => phaseSheet(gp, i - 1, pool));
  $("#ph-next")?.addEventListener("click", () => phaseSheet(gp, i + 1, pool));
}

const josa2 = (name) => { const c = name.charCodeAt(name.length - 1) - 0xac00; return `${name}${c >= 0 && c <= 11171 && c % 28 ? "을" : "를"}`; };

function detailSheet(b, pool, my) {
  const cards = b.cards.map((c) => `<section class="card" style="background:var(--bg-layer)">
      <div class="eyebrow">${esc(c.title)}</div><div class="title" style="font-size:var(--t5)">${linkify(c.headline)}</div>
      <ul class="plain">${c.items.map((i) => `<li class="${i.kind}">${linkify(i.text)}${evChips(i.evidence, pool)}</li>`).join("")}</ul></section>`).join("");
  const paths = b.paths && b.paths.mine && b.paths.mine.length ? timetable(b.paths) : "";
  const outside = b.picks_outside.length ? `<h2 class="section">내 챔프폭 밖에서 확실히 나은 픽</h2><div class="list">${b.picks_outside.map((r) => pickRow(r, my)).join("")}</div>` : "";
  openSheet(`<h2>근거와 세부</h2><p class="sub">게임 시작 전이나 로딩 화면에서 천천히 봐도 돼요.</p>
    ${b.notes.map((n) => `<p class="sub">${linkify(n)}</p>`).join("")}
    ${cards}${outside}${paths}`, { wide: true });
}

const REGION = { own_jungle: "우리 정글", enemy_jungle: "상대 정글", river: "강가", top: "탑", mid: "미드", bot: "봇", base: "본진" };
const MONSTER = { DRAGON: "드래곤", HORDE: "공허 유충", RIFTHERALD: "전령", BARON_NASHOR: "바론" };
function evSay(e) {
  if (e.kind === "recall") return e.t < 150 ? "상점 구매 (귀환인지는 확실하지 않아요)" : "귀환";
  if (e.kind === "death_back") return "죽고 나서 구매";
  if (e.kind === "death") return `죽었어요 · ${REGION[e.where] || ""}`;
  if (e.kind === "kill") return `킬 · ${REGION[e.where] || ""}`;
  if (e.kind === "assist") return `어시스트 · ${REGION[e.where] || ""}`;
  if (e.kind === "objective") return `${e.ours ? "우리" : "상대"} ${MONSTER[e.monster] || e.monster}`;
  return e.kind;
}
function timetable(paths) {
  const col = (rec, name) => {
    const rows = rec.minutes.map((p) => ({ t: p.m * 60, h: `<span class="tl-t num">${p.m}:00</span><span>캠프 <b class="num">${p.camps}</b>개 <span class="sub">· 그 순간 ${REGION[p.region] || ""}</span></span>` }));
    for (const e of rec.events) rows.push({ t: e.t, h: `<span class="tl-t num strong">${mmss(e.t)}</span><span><b>${esc(evSay(e))}</b></span>` });
    return `<div><div class="eyebrow">${esc(name)}</div><ol class="tl">${rows.sort((a, b) => a.t - b.t).map((r) => `<li>${r.h}</li>`).join("")}</ol></div>`;
  };
  const m = paths.mine[0];
  return `<h2 class="section">고티어 실제 한 판의 첫 6분<small>정확한 시각은 귀환·킬·오브젝트뿐이에요</small></h2>
    <div class="tl-grid">${col(m, `나 · ${m.label} (고티어 ${m.games}판 중 대표)`)}${paths.enemy ? col(paths.enemy, `상대 · ${paths.enemy.name}`) : ""}</div>`;
}

function aiSheet(ai, pool) {
  if (!ai || ai.status !== "ok") { openSheet(`<h2>AI 코치</h2><p class="body">${esc(ai?.message || "정리하는 중이에요. 10~20초 걸려요.")}</p>`); return; }
  openSheet(`<div class="eyebrow">AI 코치 · 근거가 있는 말만 남겼어요</div><h2>${linkify(ai.headline)}</h2>
    <div class="list" style="margin-top:12px">${ai.points.map((p) => row({ lead: `<span class="tag">${esc(p.phase)}</span>`, title: linkify(p.text) + evChips(p.evidence, pool) })).join("")}</div>`, { wide: true });
}
