/* 홈: "나 지금 어디쯤이야?" 하나에 답하고, 다음에 고칠 것 하나만 제안한다.
 * H1 숫자 하나 히어로 · H2 진행도는 플래티넘→챌린저 한 줄 · H3 제안은 하나 · H4 제안(떠 있는 층)과 기록(리스트) 분리
 * H5 장식 없이 글·버튼으로 위계 · H6 성공 = 다음 판에 지표가 바뀌었나(전·후 값 표시) */
import { $, api, badge, champImg, champKey, champName, ensureChamps, ensureLearn, empty, esc, go, GROUP_KO, mmss, openReplay,
  openSheet, post, put, row, skeleton, state, toast } from "./core.js";
import { startSync } from "./review.js";
import { startSrs } from "./flows.js";

export async function renderHome(view) {
  view.innerHTML = `<div class="page">${skeleton(2)}</div>`;
  await Promise.all([ensureChamps(), ensureLearn().catch(() => {})]);
  const [h, g, games] = await Promise.all([api("/api/home"), api("/api/gap").catch(() => ({ ready: false })),
    api("/api/review/matches").catch(() => [])]);
  state.home = h;
  const page = document.createElement("div");
  page.className = "page";

  if (!g.ready) {
    // L4·Value first: 설정부터 시키지 않고, 바로 할 수 있는 한 가지(경기 불러오기)만
    page.innerHTML = `<div class="top"><h1>반가워요</h1><p>최근 경기를 불러오면 챌린저와 무엇이 다른지 바로 보여 드려요.</p></div>
      <div class="card suggest">${empty({ em: "🎯", title: "내 경기부터 불러올게요",
        desc: "롤 클라이언트가 켜져 있으면 API 키 없이 최근 솔랭을 가져와요. 한 판에 2~3초 걸려요.",
        action: `<button class="btn fill" id="sync">최근 경기 불러오기</button>` })}</div>
      <p class="sub" style="text-align:center;margin-top:16px">${esc(g.reason || "")}</p>`;
    view.replaceChildren(page);
    $("#sync", page).onclick = () => startSync({ onDone: () => renderHome(view) });
    return;
  }

  const top = g.gaps[0];
  const delta = g.progress_before != null ? g.progress_now - g.progress_before : null;
  const focus = h.focus && h.focus.graded !== false ? h.focus : null;
  const fh = focus ? focus.history.filter((x) => x.status !== "na") : [];

  page.innerHTML = `
    ${h.rank ? `<div class="eyebrow">지금 랭크 · ${esc(h.rank)}</div>` : ""}
    <section class="hero" aria-label="챌린저까지 진행도">
      <div class="hero-num num">${g.progress}<small>점</small></div>
      <div class="hero-cap">플래티넘을 0점, 챌린저를 100점으로 놓고 내 최근 ${g.games}판을 쟀어요${delta != null
        ? ` · <span class="delta ${delta >= 0 ? "up" : "down"}">${delta >= 0 ? "+" : ""}${delta}점</span> <span class="sub">(앞쪽 판보다)</span>` : ""}</div>
      <div class="bar" style="margin-top:20px"><i style="width:${Math.max(2, Math.min(100, g.progress))}%"></i></div>
      <div class="scale"><span>플래티넘 0</span><span>챌린저 100</span></div>
    </section>

    ${top ? `<section class="card suggest" style="margin-top:32px" aria-label="이번 주에 고칠 것">
      <div class="eyebrow">이번 주엔 이것 하나만 고쳐 봐요</div>
      <div class="title" style="font-size:var(--t3);line-height:var(--t3-lh)">${esc(top.label)}</div>
      <div class="body" style="margin-top:8px">지금 <b class="num">${esc(top.mine_text)}</b>${top.range_text ? ` <span class="sub">(판마다 ${esc(top.range_text)})</span>` : ""}, 챌린저는 <b class="num accent">${esc(top.target_text)}</b>예요.
        이번 주는 <b class="num">${esc(top.step_text)}</b>까지만 가 봐요.</div>
      <div class="body" style="margin-top:12px;color:var(--grey900)">다음 판 다짐: 만약 ${esc(top.if_then || top.drill)}</div>
      <div class="btn-row">
        ${top.examples && top.examples.length ? `<button class="btn fill" id="watch">${esc(top.examples[0].player)}가 하는 거 보기</button>` : ""}
        <button class="btn weak" id="why">왜 이게 1순위예요?</button>
      </div>
    </section>` : `<section class="card suggest" style="margin-top:32px">${empty({ em: "👏", title: "검증된 지표는 모두 챌린저 수준이에요",
      desc: "판이 더 쌓이면 다시 비교해 드릴게요." })}</section>`}

    <h2 class="section">내 기록</h2>
    <div class="list">
      ${h.due ? row({ lead: "🔁", title: `복습할 장면 ${h.due}개가 기다려요`, sub: "틀렸던 판단을 잊을 때쯤 다시 풀어요", attrs: 'data-act="srs"' }) : ""}
      ${focus ? row({ lead: "🎯", title: `연습 목표 · ${esc(focus.title)}`,
        sub: fh.length ? `최근 ${fh.length}판 중 ${fh.filter((x) => x.status === "pass").length}번 지켰어요` : "아직 기록이 없어요. 한 판 하면 체크해 드려요",
        attrs: 'data-act="focus"' })
        : row({ lead: "🎯", title: "연습 목표 정하기", sub: "한 번에 하나만 연습하는 게 가장 빨라요", attrs: 'data-act="pick"' })}
      ${games.slice(0, 3).map((m) => row({ lead: champImg(champKey(m.champion_id)) || "?", title: `${esc(champName(m.champion_id))} · ${m.win ? "승리" : "패배"}`,
        sub: `${m.kills}/${m.deaths}/${m.assists} · ${fmtDate(m.game_start)}`,
        end: m.focus_status === "pass" ? badge("목표 달성", "green") : m.focus_status === "fail" ? badge("목표 미달", "red") : "",
        href: `#/review/${m.match_id}` })).join("")}
      ${h.ai_ready ? row({ lead: "🧭", title: "이번 주 AI 리포트", sub: "진단·체크·판단 훈련 기록으로 이번 주 연습 계획을 짜 드려요", attrs: 'data-act="weekly"' }) : ""}
      ${row({ lead: "＋", title: "새 경기 불러오기", sub: "방금 한 판은 게임이 끝나면 자동으로 들어와요", attrs: 'data-act="sync"' })}
    </div>

    ${g.by_champion && g.by_champion.length ? `<h2 class="section">챔피언별 진행도<small>3판 이상</small></h2>
      <div class="list">${g.by_champion.slice(0, 5).map((c) => row({ lead: champImg(c.key) || "?", title: esc(c.name),
        sub: `${c.wins}승 ${c.games - c.wins}패`, end: `<div class="val num">${c.progress}점</div>` })).join("")}</div>
      <p class="sub" style="margin-top:8px">점수가 높은 챔피언일수록 고수처럼 플레이하고 있어요. 랭크에선 이 챔피언을 먼저 골라 보세요.</p>` : ""}`;
  view.replaceChildren(page);

  $("#watch", page)?.addEventListener("click", () => openReplay(top.examples[0].match_id, Math.round(top.examples[0].t), top.watch));
  $("#why", page)?.addEventListener("click", () => gapSheet(g, top));
  page.addEventListener("click", async (e) => {
    const a = e.target.closest("[data-act]")?.dataset.act;
    if (a === "srs") startSrs(() => renderHome(view));
    if (a === "focus") focusSheet(focus);
    if (a === "pick") pickFocusSheet(() => renderHome(view));
    if (a === "sync") startSync({ onDone: () => renderHome(view) });
    if (a === "weekly") weeklySheet();
  });
}

/** 주간 리포트: Claude 가 근거 id 를 붙인 문장만 보여 준다 (근거 없는 문장은 서버에서 버림) */
async function weeklySheet() {
  const sh = openSheet(`<h2>이번 주 계획을 짜는 중이에요</h2><p class="body">Claude가 최근 기록을 읽고 있어요. 30초쯤 걸려요.</p>${skeleton(2)}`);
  let r;
  try { r = await post("/api/coach/weekly"); } catch (e) { r = { status: "error", message: e.message }; }
  if (r.status !== "ok") {
    sh.innerHTML = `<button class="close" aria-label="닫기" data-close>✕</button><h2>리포트를 만들지 못했어요</h2>
      <p class="body">${esc(r.message || "")}</p><div class="btn-row end"><button class="btn grey m" data-close>닫기</button></div>`;
    return;
  }
  const ev = Object.fromEntries((r.evidence || []).map((e) => [e.id, e]));
  sh.innerHTML = `<button class="close" aria-label="닫기" data-close>✕</button><div class="eyebrow">이번 주 AI 리포트</div>
    <h2>${esc(r.headline || "이번 주 계획")}</h2>
    <div class="list" style="margin-top:16px">${r.points.map((p) => row({ title: esc(p.phase), sub: esc(p.text) })).join("")}</div>
    <details style="margin-top:16px"><summary class="sub">근거로 쓴 기록 보기</summary>
      <ul class="plain">${[...new Set(r.points.flatMap((p) => p.evidence))].map((id) => `<li class="sub">${esc(ev[id]?.text || id)}</li>`).join("")}</ul></details>
    <div class="btn-row end"><button class="btn grey m" data-close>닫기</button></div>`;
}

const fmtDate = (s) => { const d = new Date(String(s).replace(" ", "T")); return isNaN(d) ? "" : `${d.getMonth() + 1}월 ${d.getDate()}일 ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`; };
export { fmtDate };

/** 왜 1순위인지: 티어 사다리 + 가르는 힘 + 다른 후보 (B2: 근거는 펼쳤을 때만) */
function gapSheet(g, top) {
  const ladder = (x) => ["platinum", "emerald", "diamond", "apex", "challenger", "pro"].filter((k) => x.groups_text[k])
    .map((k) => row({ title: GROUP_KO[k], end: `<div class="val num">${esc(x.groups_text[k])}</div>` })).join("");
  const sh = openSheet(`<h2>${esc(top.label)}</h2>
    <p class="body">고수(프로·챌린저·마스터+)와 플래티넘 경기를 비교했을 때 이 지표가 실력을 크게 갈랐고, 지금 내가 챌린저와 가장 멀리 떨어져 있어요.
      이긴 판끼리, 진 판끼리 따로 봐도 차이가 남은 지표만 골랐어요.</p>
    <div class="list" style="margin-top:16px">${row({ title: "나", sub: top.range_text ? `판마다 ${esc(top.range_text)} · 최근 ${top.games}판 중앙값` : `최근 ${top.games}판 중앙값`, end: `<div class="val num accent">${esc(top.mine_text)}</div>` })}${ladder(top)}</div>
    ${top.within ? `<div class="card" style="margin-top:12px;background:var(--bg-layer)"><div class="eyebrow">같은 사람 안에서 비교하면</div>
      <p class="body" style="margin:4px 0 0">${top.lever
        ? `플레이어 ${top.within.players}명의 ${top.within.games}판에서, 이 지표가 자기 평소보다 좋았던 판의 승률이 <b>${Math.round(top.within.win_diff * 100)}%p</b> 높았어요.`
        : `플레이어 ${top.within.players}명의 판을 비교하면, 이 지표가 좋았던 판에 더 이기지는 않았어요. 고수의 습관을 보여 주는 표시라서 우선순위를 낮췄어요.`}</p>
      <p class="sub" style="margin:6px 0 0">이기는 판이라 지표가 좋아졌을 수도 있어서, 원인이라고 단정하지는 않아요.</p></div>` : ""}
    ${top.concept === "communication-pings" ? `<p class="sub" style="margin-top:12px">핑 숫자 자체가 목표는 아니에요. 핑을 치려면 미니맵을 보고 있어야 해서, 맵을 보는 습관이 숫자로 드러나는 거예요.</p>` : ""}
    ${top.examples && top.examples.length > 1 ? `<h2 class="section" style="margin-top:28px">프로가 하는 거 보기<small>같은 패치 리플레이</small></h2>
      ${top.watch ? `<p class="sub" style="margin:0 0 8px">보면서 할 일: ${esc(top.watch)}</p>` : ""}<div class="list">${top.examples.map((e, i) => row({ lead: "▶", title: `${esc(e.player)} · ${esc(e.champion)}`, sub: `이 판 ${esc(e.value_text)}`, attrs: `data-ex="${i}"` })).join("")}</div>` : ""}
    ${g.gaps.length > 1 ? `<h2 class="section" style="margin-top:28px">그다음 후보</h2><div class="list">${g.gaps.slice(1).map((x) =>
      row({ title: esc(x.label), sub: `나 ${esc(x.mine_text)} · 챌린저 ${esc(x.target_text)}` })).join("")}</div>` : ""}
    <div class="btn-row end"><button class="btn grey m" data-close>닫기</button>
      ${state.home?.skills?.some((s) => s.id === top.concept) ? `<button class="btn fill m" id="set">연습 목표로 정하기</button>` : ""}</div>`);
  sh.addEventListener("click", (e) => {
    const i = e.target.closest("[data-ex]")?.dataset.ex;
    if (i != null) openReplay(top.examples[+i].match_id, Math.round(top.examples[+i].t), top.watch);
  });
  $("#set", sh)?.addEventListener("click", async () => { await put("/api/focus", { concept: top.concept }); toast("연습 목표로 정했어요"); go("#/home"); });
}

function focusSheet(f) {
  const hist = f.history.filter((x) => x.status !== "na");
  const sh = openSheet(`<div class="eyebrow">연습 목표</div><h2>${esc(f.title)}</h2>
    <p class="body">${esc(f.goal || "")}</p>
    ${hist.length ? `<div class="list" style="margin-top:16px">${hist.slice(0, 8).map((x) => row({
      lead: x.status === "pass" ? "✓" : "✗", title: `${esc(x.champion || "")} · ${x.status === "pass" ? "지켰어요" : "놓쳤어요"}`, sub: esc(x.value) })).join("")}</div>`
      : `<p class="sub">아직 기록이 없어요. 한 판 하면 자동으로 체크해 드려요.</p>`}
    <div class="btn-row end"><button class="btn grey m" id="change">다른 목표로 바꾸기</button><a class="btn weak m" href="#/learn/${f.id}">설명 보기</a></div>`);
  $("#change", sh).onclick = () => pickFocusSheet(() => go("#/home"));
}

export function pickFocusSheet(after) {
  const h = state.home;
  const sh = openSheet(`<h2>무엇을 연습할까요?</h2><p class="sub">경기 기록으로 지켰는지 체크할 수 있는 것만 골랐어요. 약한 것부터 보여 드려요.</p>
    <div class="list" style="margin-top:16px">${(h?.skills || []).map((s) => row({ title: esc(s.title),
      sub: esc(s.goal), end: s.total ? `<div class="sub num">${s.pass}/${s.total}판</div>` : "", attrs: `data-id="${s.id}"` })).join("")}</div>`);
  sh.addEventListener("click", async (e) => {
    const id = e.target.closest("[data-id]")?.dataset.id;
    if (!id) return;
    await put("/api/focus", { concept: id });
    toast("연습 목표로 정했어요");
    after?.();
  });
}
