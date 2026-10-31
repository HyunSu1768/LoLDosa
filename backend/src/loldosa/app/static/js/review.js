/* 경기 복기: 이 판을 가른 장면 하나 → 그 순간 고수라면? → 실력 지표 → (펼치면) 나머지.
 * R1 핵심 장면 맨 위 · R2 졌을 땐 공감 한 줄 · R3 "~해 보세요" 제안형 · R5 진행 3단계 · R6 그림엔 결론 문장
 * One thing per page: 판단 훈련은 한 번에 한 장면 */
import { $, $$, api, badge, champImg, champKey, champName, empty, ensureChamps, ensureLearn, esc, evChips, go, linkify, mmss,
  openReplay, openSheet, closeSheet, post, put, row, signed, skeleton, state, toast, comma } from "./core.js";
import { fmtDate } from "./home.js";

/* ---------- 경기 불러오기: 3단계 진행 (R5) ---------- */
export async function startSync({ onDone } = {}) {
  const steps = ["경기 불러오는 중", "분석하는 중", "다 됐어요"];
  const sh = openSheet(`<h2>최근 경기를 가져올게요</h2><ol class="steps3">${steps.map((s, i) => `<li data-i="${i}">${s}</li>`).join("")}</ol>
    <p class="sub" id="sync-msg">롤 클라이언트가 켜져 있으면 API 키 없이 가져와요.</p>`);
  const mark = (i) => $$(".steps3 li", sh).forEach((li) => { li.classList.toggle("on", +li.dataset.i === i); li.classList.toggle("done", +li.dataset.i < i); });
  mark(0);
  try {
    const key = await api("/api/riot-key").catch(() => ({ set: false }));
    const t = setTimeout(() => mark(1), 2500);
    const list = key.set && !key.problem ? await post("/api/review/sync", { count: 20 }) : await post("/api/review/sync-lcu", { count: 20 });
    clearTimeout(t); mark(2);
    $("#sync-msg", sh).textContent = `${list.length}판을 분석했어요.`;
    setTimeout(() => { closeSheet(); onDone?.(list); }, 700);
  } catch (e) {
    // S2: 상황 → 원인 → 한 번에 고치는 버튼
    sh.innerHTML = `<button class="close" aria-label="닫기" data-close>✕</button><h2>경기를 가져오지 못했어요</h2>
      <p class="body">${esc(e.message)}</p>
      <p class="sub">롤 클라이언트를 켜고 다시 시도하거나, 설정에서 Riot API 키를 넣으면 클라이언트 없이도 가져올 수 있어요.</p>
      <div class="btn-row end"><a class="btn grey m" href="#/settings" data-close>키 넣으러 가기</a><button class="btn fill m" id="retry">다시 가져오기</button></div>`;
    $("#retry", sh).onclick = () => startSync({ onDone });
  }
}

/* ---------- 목록 ---------- */
export async function renderReviewList(view) {
  view.innerHTML = `<div class="page">${skeleton(3)}</div>`;
  await ensureChamps();
  const list = await api("/api/review/matches");
  view.innerHTML = `<div class="page">
    <div class="top"><h1>경기 복기</h1><p>판마다 하나만 배워요. 게임이 끝나면 자동으로 들어와요.</p></div>
    ${list.length ? `<div class="list">${list.map((m) => row({ lead: champImg(champKey(m.champion_id)) || "?",
      title: `${esc(champName(m.champion_id))} · <span class="${m.win ? "good" : "bad"}">${m.win ? "승리" : "패배"}</span>`,
      sub: `${m.position === "JUNGLE" ? "" : "정글이 아닌 판 · "}${m.kills}/${m.deaths}/${m.assists} · ${fmtDate(m.game_start)}`,
      end: m.focus_status === "pass" ? badge("목표 달성", "green") : m.focus_status === "fail" ? badge("목표 미달", "red") : "",
      href: `#/review/${m.match_id}` })).join("")}</div>
      <div class="btn-row"><button class="btn weak" id="sync">새 경기 불러오기</button></div>`
      : empty({ em: "🎮", title: "아직 불러온 경기가 없어요", desc: "최근 솔랭을 가져오면 판마다 고칠 점 하나를 알려 드려요.",
        action: `<button class="btn fill" id="sync">최근 경기 불러오기</button>` })}</div>`;
  $("#sync", view).onclick = () => startSync({ onDone: () => renderReviewList(view) });
}

/* ---------- 상세 ---------- */
export async function renderReview(view, id) {
  view.innerHTML = `<div class="page">${skeleton(3)}</div>`;
  await Promise.all([ensureChamps(), ensureLearn().catch(() => {})]);
  let rv;
  try { rv = await api(`/api/review/${id}`); } catch (e) {
    view.innerHTML = `<div class="page">${empty({ em: "😵", title: "이 경기를 분석하지 못했어요", desc: esc(e.message), action: `<a class="btn grey" href="#/review">목록으로</a>` })}</div>`;
    return;
  }
  const pool = Object.fromEntries(rv.evidence.map((e) => [e.id, e]));
  const sm = rv.summary, kl = rv.key_lesson;
  const focus = rv.checks.find((c) => c.focus && c.status !== "na");
  const feel = sm.win ? "잘 이겼어요." : "아쉬운 판이었어요.";  // R2
  const graded = rv.checks.filter((c) => c.status !== "na");
  const gapBad = (rv.gap || []).filter((x) => !x.ok);

  view.innerHTML = `<div class="page">
    <a class="back" href="#/review">← 경기 목록</a>
    <div class="rv-head">${champImg(sm.key, sm.champion)}<div>
      <div class="title" style="font-size:var(--t4)">${esc(sm.champion)} · <span class="${sm.win ? "good" : "bad"}">${sm.win ? "승리" : "패배"}</span></div>
      <div class="sub">${esc(sm.kda)} · ${esc(sm.duration)} · ${esc(sm.date)}${sm.enemy_jungler ? ` · 상대 정글 ${esc(sm.enemy_jungler)}` : ""}</div></div>
      ${focus ? `<div class="rv-focus">${badge(focus.status === "pass" ? "연습 목표 달성" : "연습 목표 미달", focus.status === "pass" ? "green" : "red")}</div>` : ""}</div>

    <section class="hero">
      <div class="eyebrow">${feel} 이 판에서 하나만 배운다면</div>
      ${kl ? `<div class="brief-hero">${esc(kl.lesson.title)}</div>
        <p class="body" style="margin-top:12px">${linkify(kl.lesson.text)}${evChips(kl.lesson.evidence, pool)}</p>
        <div class="btn-row">
          ${kl.lesson.t != null ? `<button class="btn fill" id="replay">이 장면 리플레이로 보기</button>` : ""}
          <a class="btn weak" href="#/learn/${kl.concept.id}">${esc(kl.concept.title)} 배우기</a>
        </div>` : `<div class="brief-hero">${rv.is_jungle ? "눈에 띄는 큰 실수가 없었어요" : "정글로 뛴 판이 아니라 간단히만 볼게요"}</div>`}
    </section>

    <div id="moments"></div>

    ${rv.gap && rv.gap.length ? `<h2 class="section">이번 판 실력 지표<small>고수와 플래티넘을 실제로 가르는 것만</small></h2>
      <p class="sub" style="margin:-4px 0 12px">${gapBad.length ? `${rv.gap.length}개 중 ${gapBad.length}개가 고수 기준선에 못 미쳤어요.` : "모든 지표가 고수 기준선을 넘었어요."}</p>
      <div class="list">${[...gapBad, ...rv.gap.filter((x) => x.ok)].slice(0, 5).map((x) => row({ title: esc(x.label),
        sub: `기준선 ${x.higher_better ? "" : "≤ "}${esc(x.threshold_text)}${x.higher_better ? " 이상" : ""} · 챌린저 ${esc(x.challenger_text)}`,
        end: `<div class="val num ${x.ok ? "good" : "bad"}">${esc(x.mine_text)}</div>`, href: `#/learn/${x.concept}` })).join("")}</div>` : ""}

    ${rv.live && rv.live.samples > 10 ? `<h2 class="section">초 단위 기록<small>게임 중 내 PC에서 기록 · 15분까지</small></h2>
      <div class="list">
        ${rv.live.text.levels ? row({ title: "레벨 찍은 시각", sub: esc(rv.live.text.levels) }) : ""}
        ${rv.live.text.shops ? row({ title: "상점(귀환)", sub: esc(rv.live.text.shops) }) : ""}
        ${row({ title: "1,200골드 넘게 들고 버틴 시간", sub: rv.live.rich_s >= 60 ? "1,200골드가 모이면 싸우기 전에 귀환해 보세요" : "괜찮았어요",
          end: `<div class="val num ${rv.live.rich_s >= 60 ? "bad" : ""}">${Math.floor(rv.live.rich_s / 60)}분 ${rv.live.rich_s % 60}초</div>` })}
        ${rv.live.text.idle ? row({ title: "CS·킬 관여가 1분 넘게 멈춘 구간", sub: `${esc(rv.live.text.idle)} · 이동이나 시야 작업이었는지 리플레이로 확인해 보세요` }) : ""}
      </div>` : ""}

    <div class="btn-row" style="margin-top:32px">
      <button class="btn grey" id="more">나머지 기록 보기</button>
      <button class="btn grey" id="ai">AI 코치에게 물어보기</button>
    </div>
  </div>`;

  $("#replay", view)?.addEventListener("click", () => openReplay(id, kl.lesson.t));
  $("#more", view).onclick = () => moreSheet(rv, pool, graded);
  $("#ai", view).onclick = () => aiSheet(id, pool);
  loadMoments(id, $("#moments", view));
}

function moreSheet(rv, pool, graded) {
  const kl = rv.key_lesson;
  const others = rv.lessons.filter((l) => !kl || l.title !== kl.lesson.title);
  const info = rv.checks.filter((c) => c.info);
  openSheet(`<h2>나머지 기록</h2>
    ${graded.length ? `<h2 class="section">목표 체크</h2><div class="list">${graded.map((c) => row({ lead: c.status === "pass" ? "✓" : "✗",
      title: esc(c.title), sub: esc(c.value), href: `#/learn/${c.concept}` })).join("")}</div>` : ""}
    ${others.length ? `<h2 class="section">그 밖에 고칠 점</h2><div class="list">${others.map((l) => row({ title: esc(l.title),
      sub: linkify(l.text) + evChips(l.evidence, pool) })).join("")}</div>` : ""}
    ${rv.strengths.length ? `<h2 class="section">잘한 점</h2><div class="chips">${rv.strengths.map((l) => badge(`✓ ${l.title}`, "green")).join(" ")}</div>` : ""}
    ${info.length ? `<h2 class="section">참고 기록<small>고수와 플래티넘 차이가 없어서 채점하지 않아요</small></h2>
      <div class="list">${info.map((c) => row({ title: esc(c.title), sub: esc(c.info) })).join("")}</div>` : ""}
    ${rv.metrics.length ? `<h2 class="section">비교표</h2><div class="list">${rv.metrics.map((m) => row({ title: linkify(m.label),
      sub: `내 평균 ${esc(m.me_avg || "-")} · 다음 티어 ${esc(m.target || "-")} · 고티어 ${esc(m.bench)}`, end: `<div class="val num ${m.verdict}">${esc(m.mine)}</div>` })).join("")}</div>` : ""}
    ${rv.moments.length ? `<h2 class="section">정확한 시각이 있는 사건</h2><ol class="tl">${rv.moments.map((m) =>
      `<li class="${m.good === true ? "good" : m.good === false ? "bad" : ""}"><span>${linkify(m.text)}</span></li>`).join("")}</ol>` : ""}`, { wide: true });
}

async function aiSheet(id, pool) {
  const sh = openSheet(`<h2>AI 코치가 정리하는 중이에요</h2><p class="sub">10~20초 걸려요. 근거가 있는 말만 남겨요.</p><div class="sk card"></div>`);
  try {
    const r = await post(`/api/review/${id}/ai`);
    sh.innerHTML = r.status === "ok" ? `<button class="close" aria-label="닫기" data-close>✕</button><div class="eyebrow">AI 코치</div><h2>${linkify(r.headline)}</h2>
      <div class="list" style="margin-top:12px">${r.points.map((p) => row({ lead: `<span class="tag">${esc(p.phase)}</span>`, title: linkify(p.text) + evChips(p.evidence, pool) })).join("")}</div>`
      : `<button class="close" aria-label="닫기" data-close>✕</button><h2>AI 코치를 쓸 수 없어요</h2><p class="body">${esc(r.message || "")}</p>`;
  } catch (e) { sh.innerHTML = `<button class="close" aria-label="닫기" data-close>✕</button><h2>AI 코치를 쓸 수 없어요</h2><p class="body">${esc(e.message)}</p>`; }
}

/* ---------- 그 순간 고수라면? (한 번에 한 장면) ---------- */
async function loadMoments(matchId, box) {
  let list = [];
  try { list = await api(`/api/review/${matchId}/moments`); } catch { return; }
  if (!list.length) return;
  let i = 0;
  const draw = () => {
    const mo = list[i];
    box.innerHTML = `<h2 class="section">그 순간, 고수라면?<small>${i + 1} / ${list.length}</small></h2>
      <section class="card moment">
        <div class="eyebrow num">${mo.minute}:00 · ${esc(mo.reason)}</div>
        <div class="mo-grid">${board(mo.snapshot)}
          <div><ul class="plain">${mo.snapshot.facts.map((f) => `<li>${linkify(f)}</li>`).join("")}</ul>
            <div class="title" style="margin:16px 0 8px">여기서 뭐 할래요?</div>
            <div class="choices">${mo.choices.map((c) => `<button class="choice" data-a="${c.action}">${esc(c.label)}</button>`).join("")}</div>
            <div class="reveal"></div></div></div>
      </section>
      <div class="btn-row end">${i > 0 ? `<button class="btn grey m" data-nav="-1">이전 장면</button>` : ""}${i < list.length - 1 ? `<button class="btn weak m" data-nav="1">다음 장면</button>` : ""}</div>`;
    $$(".choice", box).forEach((b) => (b.onclick = () => reveal(matchId, mo, box, b.dataset.a)));
    $$("[data-nav]", box).forEach((b) => (b.onclick = () => { i += +b.dataset.nav; draw(); }));
  };
  draw();
}

function reveal(matchId, mo, box, choice) {
  if (box.dataset.done === `${mo.minute}`) return;
  box.dataset.done = `${mo.minute}`;
  const good = mo.good.includes(choice);
  $$(".choice", box).forEach((b) => {
    if (mo.good.includes(b.dataset.a)) b.classList.add("right");
    else if (b.dataset.a === choice) b.classList.add("wrong");
    b.disabled = true;
  });
  const bars = mo.crowd.slice(0, 5).map((c) => `<div class="crowd ${c.action === choice ? "picked" : ""}">
      <span>${esc(c.label)}</span><span class="bar"><i style="width:${Math.round(c.share * 100)}%"></i></span><span class="num">${Math.round(c.share * 100)}%</span>
      <span class="sub num">팀 골드 ${signed(c.swing)}</span></div>`).join("");
  $(".reveal", box).innerHTML = `<div class="verdict ${good ? "good" : "bad"}">${good ? "좋은 선택이에요" : "고수는 다르게 많이 골랐어요"}</div>
    <p class="sub">${esc(mo.verdict)}</p>
    <div class="sub" style="margin:12px 0 6px">비슷한 상황의 ${esc(mo.pool_label)} 정글러 ${mo.k}명이 한 것 · 2분 뒤 팀 골드</div>${bars}
    <p class="sub" style="margin-top:8px">실제로 나는 ${esc(mo.mine.label)}를 골랐고, 2분 뒤 팀 골드는 ${signed(mo.mine.swing)}${mo.mine.died ? " · 내가 죽었어요" : ""}</p>
    <div class="btn-row"><button class="btn weak s" id="mo-replay">이 장면 리플레이로 보기</button></div>`;
  $("#mo-replay", box).onclick = () => openReplay(matchId, mo.t);
  post("/api/moments/answer", { match_id: matchId, minute: mo.minute, choice, good, concepts: mo.concepts.map((c) => c.id),
    moment: { match_id: matchId, minute: mo.minute, t: mo.t, reason: mo.reason, snapshot: mo.snapshot, choices: mo.choices,
      crowd: mo.crowd.slice(0, 6), good: mo.good, verdict: mo.verdict, mine: mo.mine, k: mo.k, pool_label: mo.pool_label, concepts: mo.concepts } }).catch(() => {});
}

/** 상황판: 우리 본진 항상 왼쪽 아래, 글자 라벨, 라인 골드 차는 색+글자 (R6: 그림 없이도 facts 로 결론 전달) */
export function board(snap, size = 300) {
  const M = 14870, flip = snap.team === 200, S = size, pad = 18;
  const X = (x) => ((flip ? M - x : x) / M) * S, Y = (y) => S - ((flip ? M - y : y) / M) * S;
  const L = snap.lanes || {};
  const cls = (v) => (v > 150 ? "win" : v < -150 ? "lose" : "even");
  const say = (v) => (v > 150 ? `+${comma(v)}` : v < -150 ? comma(v) : "비슷");
  const boxes = [];
  const toks = [...snap.units].sort((a, b) => (b.me ? 3 : b.enemy_jungler ? 2 : 0) - (a.me ? 3 : a.enemy_jungler ? 2 : 0)).map((u) => {
    const c = u.me ? "me" : u.enemy_jungler ? "ejg" : u.ally ? "ally" : "enemy";
    const text = u.me ? `나 · ${u.name}` : u.enemy_jungler ? `상대 정글 · ${u.name}` : u.name;
    const w = text.length * (u.me || u.enemy_jungler ? 9.5 : 8), cx = X(u.x), cy = Y(u.y);
    let spot = null;
    for (const [dx, dy] of [[8, 4], [8, -9], [8, 17], [-8 - w, 4], [-8 - w, -9], [8, 30]]) {
      let bx = cx + dx; if (bx + w > S - 2) bx = cx - 8 - w; if (bx < 2) bx = 2;
      const by = cy + dy - 10;
      if (!boxes.some((b) => bx < b.x + b.w && bx + w > b.x && by < b.y + 12 && by + 12 > b.y)) { spot = { x: bx, y: by }; break; }
    }
    spot = spot || { x: Math.min(cx + 8, S - w - 2), y: cy - 6 };
    boxes.push({ x: spot.x, y: spot.y, w });
    return `<g class="tok ${c}"><circle cx="${cx}" cy="${cy}" r="${u.me || u.enemy_jungler ? 6 : 4}"/><text x="${spot.x}" y="${spot.y + 10}">${esc(text)}</text></g>`;
  }).reverse().join("");
  const objs = snap.objectives.map((o) => `<text class="obj" x="${X(o.x)}" y="${Y(o.y)}" text-anchor="middle">${esc(o.name)} ${esc(o.text)}</text>`).join("");
  return `<figure class="board-wrap"><svg class="board" viewBox="0 0 ${S} ${S}" role="img" aria-label="${snap.minute}분 상황판">
    <rect width="${S}" height="${S}" rx="16" class="bg"/>
    <path d="M${pad} ${S - pad} L${pad} ${pad} L${S - pad} ${pad}" class="lane ${cls(L.top)}"/>
    <path d="M${pad} ${S - pad} L${S - pad} ${pad}" class="lane ${cls(L.mid)}"/>
    <path d="M${pad} ${S - pad} L${S - pad} ${S - pad} L${S - pad} ${pad}" class="lane ${cls(L.bot)}"/>
    <path d="M${pad + 30} ${pad + 30} L${S - pad - 30} ${S - pad - 30}" class="river"/>
    <text class="lbl ${cls(L.top)}" x="${pad + 6}" y="${pad + 14}">탑 ${say(L.top)}</text>
    <text class="lbl ${cls(L.mid)}" x="${S / 2 + 10}" y="${S / 2 - 8}">미드 ${say(L.mid)}</text>
    <text class="lbl ${cls(L.bot)}" x="${S - pad - 6}" y="${S - pad - 6}" text-anchor="end">봇 ${say(L.bot)}</text>
    ${objs}${toks}</svg>
    <figcaption class="sub">${snap.minute}:00 순간 위치 · 우리 본진은 항상 왼쪽 아래 · 라인 숫자는 우리 기준 골드 차</figcaption></figure>`;
}
