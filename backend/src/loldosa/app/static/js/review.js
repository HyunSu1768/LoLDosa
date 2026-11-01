/* 경기 복기: 이 판을 가른 장면 하나 → 그 순간 고수라면? → 실력 지표 → (펼치면) 나머지.
 * R1 핵심 장면 맨 위 · R2 졌을 땐 공감 한 줄 · R3 "~해 보세요" 제안형 · R5 진행 3단계 · R6 그림엔 결론 문장
 * One thing per page: 판단 훈련은 한 번에 한 장면 */
import { $, $$, api, badge, champImg, champKey, champName, empty, ensureChamps, ensureLearn, esc, evChips, go, linkify, mmss,
  openReplay, openSheet, closeSheet, post, put, row, signed, skeleton, state, toast, comma } from "./core.js";
import { fmtDate } from "./home.js";

/* ---------- 경기 불러오기: 3단계 진행 (R5) ---------- */
export async function startSync({ onDone, riotId = "" } = {}) {
  const steps = ["경기 불러오는 중", "분석하는 중", "다 됐어요"];
  const sh = openSheet(`<h2>최근 경기를 가져올게요</h2><ol class="steps3">${steps.map((s, i) => `<li data-i="${i}">${s}</li>`).join("")}</ol>
    <p class="sub" id="sync-msg">솔랭·자랭·일반 협곡 게임을 가져와요.</p>`);
  const mark = (i) => $$(".steps3 li", sh).forEach((li) => { li.classList.toggle("on", +li.dataset.i === i); li.classList.toggle("done", +li.dataset.i < i); });
  mark(0);
  const errors = [];
  let list = null;
  const t = setTimeout(() => mark(1), 2500);
  const key = await api("/api/riot-key").catch(() => ({ set: false }));
  // 1) 키가 있으면 Riot API (Riot ID 가 없으면 서버가 롤 클라이언트에서 내 계정을 읽음) → 2) 실패하면 롤 클라이언트 전적
  if (key.set && !key.problem) {
    $("#sync-msg", sh).textContent = "Riot 서버에서 가져와요. 처음엔 30초~1분 걸려요.";
    try { list = await post("/api/review/sync", { count: 20, riot_id: riotId }); } catch (e) { errors.push(`Riot API: ${e.message}`); }
  }
  if (!list) {
    $("#sync-msg", sh).textContent = "롤 클라이언트 전적에서 가져와요.";
    try { list = await post("/api/review/sync-lcu", { count: 20 }); } catch (e) { errors.push(`롤 클라이언트: ${e.message}`); }
  }
  clearTimeout(t);
  if (list) {
    mark(2);
    $("#sync-msg", sh).textContent = list.length ? `${list.length}판을 가져왔어요.` : "최근 협곡 게임이 없어요. 한 판 하고 다시 눌러 주세요.";
    setTimeout(() => { closeSheet(); onDone?.(list); }, list.length ? 700 : 1800);
    return;
  }
  // S2: 상황 → 원인 → 한 번에 고치는 방법 (Riot ID 로 직접 찾기)
  sh.innerHTML = `<button class="close" aria-label="닫기" data-close>✕</button><h2>경기를 가져오지 못했어요</h2>
    <ul class="plain">${errors.map((x) => `<li class="body">${esc(x)}</li>`).join("")}</ul>
    ${key.set && !key.problem ? `<p class="sub">롤 클라이언트를 못 찾았다면 Riot ID로 직접 찾을 수 있어요. PC방이라면 LoLDosa를 관리자 권한으로 실행하면 클라이언트가 잡힐 수 있어요.</p>
      <div class="field" style="margin-top:12px"><label for="rid">내 Riot ID</label><input class="input" id="rid" placeholder="닉네임#태그"></div>`
      : `<p class="sub">롤 클라이언트를 켠 뒤 다시 눌러 주세요. PC방이라면 LoLDosa를 관리자 권한으로 실행해 보세요. 설정에서 Riot API 키를 넣으면 Riot ID로도 가져올 수 있어요.</p>`}
    <div class="btn-row end"><button class="btn grey m" data-close>닫기</button><button class="btn fill m" id="retry">${key.set && !key.problem ? "이 계정으로 가져오기" : "다시 가져오기"}</button></div>`;
  $("#retry", sh).onclick = () => startSync({ onDone, riotId: $("#rid", sh)?.value.trim() || "" });
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
        ${kl.lesson.impact_say ? `<p class="sub">${esc(kl.lesson.impact_say)}</p>` : ""}
        ${kl.lesson.look && kl.lesson.t != null ? `<div class="look"><b>리플레이에서 확인할 것</b> ${esc(kl.lesson.look)}</div>` : ""}
        <div class="btn-row">
          ${kl.lesson.t != null ? `<button class="btn fill" id="replay">이 장면 리플레이로 보기</button>` : ""}
          <a class="btn weak" href="#/learn/${kl.concept.id}">${esc(kl.concept.title)} 배우기</a>
        </div>
        <div class="fb" id="fb"><span class="sub">이 교훈이 이 판에 맞나요?</span>
          <button class="btn grey s" data-fb="1">맞아요</button><button class="btn grey s" data-fb="0">아니에요</button></div>` : `<div class="brief-hero">${rv.is_jungle ? "눈에 띄는 큰 실수가 없었어요" : "정글로 뛴 판이 아니라 간단히만 볼게요"}</div>`}
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
  $$("[data-fb]", view).forEach((b) => (b.onclick = async () => {
    await post("/api/lesson/feedback", { match_id: id, rule: kl.rule, ok: b.dataset.fb === "1" }).catch(() => {});
    $("#fb", view).innerHTML = `<span class="sub">${b.dataset.fb === "1" ? "고마워요. 이런 교훈을 계속 앞에 보여 드릴게요." : "알려 줘서 고마워요. 이 규칙이 자꾸 틀리면 핵심 교훈에서 뒤로 미룰게요."}</span>`;
  }));
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
    const tr = mo.snapshot.track;
    box.dataset.done = "";
    box.innerHTML = `<h2 class="section">그 순간, 고수라면?<small>${i + 1} / ${list.length}</small></h2>
      <section class="card moment">
        <div class="eyebrow num">${mo.minute}:00 · ${esc(mo.reason)}</div>
        <div class="mo-grid"><div class="mo-map">${board(mo.snapshot)}</div>
          <div><ul class="plain">${mo.snapshot.facts.filter((f) => !f.startsWith("라인:")).map((f) => `<li>${linkify(f)}</li>`).join("")}</ul>
            ${tr ? `<div class="q-step" id="q-track"><div class="title" style="margin:16px 0 8px">1. ${esc(tr.q)}</div>
              <div class="choices">${tr.choices.map((c) => `<button class="choice" data-t="${c.id}">${esc(c.label)}</button>`).join("")}</div>
              <div class="t-reveal"></div></div>` : ""}
            <div class="q-step ${tr ? "locked" : ""}" id="q-act"><div class="title" style="margin:16px 0 8px">${tr ? "2. " : ""}여기서 뭐 할래요?</div>
              <div class="choices">${mo.choices.map((c) => `<button class="choice" data-a="${c.action}" ${tr ? "disabled" : ""}>${esc(c.label)}</button>`).join("")}</div>
              <div class="reveal"></div></div></div></div>
      </section>
      <div class="btn-row end">${i > 0 ? `<button class="btn grey m" data-nav="-1">이전 장면</button>` : ""}${i < list.length - 1 ? `<button class="btn weak m" data-nav="1">다음 장면</button>` : ""}</div>`;
    // 1단계: 상대 정글 위치 추적 (내가 볼 수 있었던 정보만으로) → 답하면 실제 위치 공개
    $$("[data-t]", box).forEach((b) => (b.onclick = () => {
      const ok = b.dataset.t === tr.answer;
      mo._trackOk = ok;
      $$("[data-t]", box).forEach((x) => { x.disabled = true; if (x.dataset.t === tr.answer) x.classList.add("right"); else if (x === b) x.classList.add("wrong"); });
      $(".t-reveal", box).innerHTML = `<div class="verdict ${ok ? "good" : "bad"}">${ok ? "맞혔어요" : "아쉬워요"}</div><p class="sub">${esc(tr.truth)}. 지도에 실제 위치를 표시했어요.</p>`;
      $(".mo-map", box).innerHTML = board(mo.snapshot, 380, true);
      $("#q-act", box).classList.remove("locked");
      $$("#q-act .choice", box).forEach((x) => (x.disabled = false));
    }));
    $$("[data-a]", box).forEach((b) => (b.onclick = () => reveal(matchId, mo, box, b.dataset.a)));
    $$("[data-nav]", box).forEach((b) => (b.onclick = () => { i += +b.dataset.nav; draw(); }));
  };
  draw();
}

function reveal(matchId, mo, box, choice) {
  if (box.dataset.done === `${mo.minute}`) return;
  box.dataset.done = `${mo.minute}`;
  const good = mo.good.includes(choice);
  $$("[data-a]", box).forEach((b) => {
    if (mo.good.includes(b.dataset.a)) b.classList.add("right");
    else if (b.dataset.a === choice) b.classList.add("wrong");
    b.disabled = true;
  });
  const bars = mo.crowd.slice(0, 5).map((c) => `<div class="crowd ${c.action === choice ? "picked" : ""}">
      <span>${esc(c.label)} ${c.best ? '<span class="badge green">결과 1위</span>' : ""}</span><span class="bar"><i style="width:${Math.round(c.share * 100)}%"></i></span><span class="num">${Math.round(c.share * 100)}%</span>
      <span class="sub">${c.score == null ? "고른 사람이 적어서 판정하지 않았어요" : esc(c.swing_say || "")}${c.died >= 0.3 ? ` · ${Math.round(c.died * 100)}%가 죽었어요` : ""}</span></div>`).join("");
  $(".reveal", box).innerHTML = `<div class="verdict ${good ? "good" : "bad"}">${good ? "고수도 많이 고른 선택이에요" : "고수는 다르게 많이 골랐어요"}</div>
    <p class="sub">${esc(mo.verdict)}</p>
    <div class="sub" style="margin:12px 0 6px">비슷한 상황의 ${esc(mo.pool_label)} 정글러 ${mo.k}명이 한 것 · 막대는 고른 비율, 아래는 2분 뒤 결과</div>${bars}
    <p class="sub" style="margin-top:8px">실제 내 선택: '${esc(mo.mine.label)}' · 2분 뒤 ${esc(mo.mine.swing_say || "")}${mo.mine.died ? " · 내가 죽었어요" : ""}</p>
    <div class="btn-row"><button class="btn weak s" id="mo-replay">이 장면 리플레이로 보기</button></div>`;
  $("#mo-replay", box).onclick = () => openReplay(matchId, mo.t);
  post("/api/moments/answer", { match_id: matchId, minute: mo.minute, choice, good, track_ok: mo._trackOk ?? null, concepts: mo.concepts.map((c) => c.id),
    moment: { match_id: matchId, minute: mo.minute, t: mo.t, reason: mo.reason, snapshot: mo.snapshot, choices: mo.choices,
      crowd: mo.crowd.slice(0, 6), good: mo.good, verdict: mo.verdict, mine: mo.mine, k: mo.k, pool_label: mo.pool_label, concepts: mo.concepts } }).catch(() => {});
}

/** 미니맵: 실제 롤 미니맵처럼 (지도 이미지 · 원형 초상화 · 아군 파랑/적 빨강/나 금색 테두리 · 방향도 게임과 같게).
 * 글자는 '나'와 '상대 정글'에만 단다 (나머지는 실제 미니맵처럼 얼굴로 알아보게). 라인 상황은 지도 밖에 아이템으로. */
export function board(snap, size = 380, reveal = false) {
  const M = 14870, S = size, R = Math.round(S * 0.042);  // 초상화 반지름
  const X = (x) => (x / M) * S, Y = (y) => S - (y / M) * S;
  const ver = state.ddragon;
  const mapUrl = ver ? `https://ddragon.leagueoflegends.com/cdn/${ver}/img/map/map11.png` : "";
  const units = [...snap.units].filter((u) => reveal || !u.hidden).sort((a, b) => (a.me ? 1 : a.enemy_jungler ? 0.5 : 0) - (b.me ? 1 : b.enemy_jungler ? 0.5 : 0));
  const tok = units.map((u, i) => {
    const cx = X(u.x), cy = Y(u.y), big = u.me || u.enemy_jungler, r = big ? R + 3 : R;
    const ring = u.me ? "var(--mm-me)" : u.ally ? "var(--mm-ally)" : "var(--mm-enemy)";
    const img = u.key && ver ? `https://ddragon.leagueoflegends.com/cdn/${ver}/img/champion/${u.key}.png` : "";
    const tag = u.me ? "나" : u.enemy_jungler ? "상대 정글" : "";
    return `<g class="mm-u"><clipPath id="c${i}"><circle cx="${cx}" cy="${cy}" r="${r}"/></clipPath>
      <circle cx="${cx}" cy="${cy}" r="${r + 2}" fill="${ring}"/>
      ${img ? `<image href="${img}" x="${cx - r}" y="${cy - r}" width="${r * 2}" height="${r * 2}" clip-path="url(#c${i})"/>` : `<circle cx="${cx}" cy="${cy}" r="${r}" fill="#333"/>`}
      ${tag ? `<g class="mm-tag ${u.me ? "me" : "ejg"}"><rect x="${cx - tag.length * 6.5 - 6}" y="${cy + r + 4}" width="${tag.length * 13 + 12}" height="20" rx="10"/>
        <text x="${cx}" y="${cy + r + 18}" text-anchor="middle">${tag}</text></g>` : ""}
      <title>${esc(u.name)}${u.hp != null ? ` · 체력 ${u.hp}%` : ""}</title></g>`;
  }).join("");
  const ls = snap.last_seen;
  const seenMark = ls && !reveal ? `<g class="mm-seen"><circle cx="${X(ls.x)}" cy="${Y(ls.y)}" r="${R + 3}"/><text x="${X(ls.x)}" y="${Y(ls.y) + 5}" text-anchor="middle">?</text>
      <g class="mm-tag ejg"><rect x="${X(ls.x) - 62}" y="${Y(ls.y) + R + 6}" width="124" height="20" rx="10"/><text x="${X(ls.x)}" y="${Y(ls.y) + R + 20}" text-anchor="middle">상대 정글 ${mmss(ls.t)}에 봄</text></g></g>` : "";
  const objs = snap.objectives.map((o) => `<g class="mm-obj"><rect x="${X(o.x) - 46}" y="${Y(o.y) - 11}" width="92" height="22" rx="11"/>
    <text x="${X(o.x)}" y="${Y(o.y) + 5}" text-anchor="middle">${esc(o.name)} ${esc(o.text)}</text></g>`).join("");
  const li = snap.lane_items || {};
  const ITEM = (id) => (ver && id ? `<img class="mm-item" src="https://ddragon.leagueoflegends.com/cdn/${ver}/img/item/${id}.png" alt="">` : "");
  const lane = (k, name) => {
    const x = li[k] || {};
    const n = Math.min(4, Math.ceil(x.count || 0));
    const icons = x.item ? Array.from({ length: n }, () => ITEM(x.item)).join("") : "";
    return `<li class="${!x.count ? "even" : x.ahead ? "win" : "lose"}"><b>${name}</b><span>${esc(x.say || "-")}</span><span class="icons">${icons}</span></li>`;
  };
  return `<figure class="minimap-wrap">
    <svg class="minimap" viewBox="0 0 ${S} ${S}" role="img" aria-label="${snap.minute}분 미니맵">
      ${mapUrl ? `<image href="${mapUrl}" width="${S}" height="${S}" preserveAspectRatio="none"/>` : `<rect width="${S}" height="${S}" fill="#0b1a14"/>`}
      <rect width="${S}" height="${S}" fill="none" stroke="#c8aa6e" stroke-width="3"/>
      ${objs}${seenMark}${tok}</svg>
    <figcaption class="sub">${snap.minute}:00 순간 위치${reveal ? "" : " · 상대 정글은 마지막으로 본 곳(?)만"} · 우리 팀은 ${snap.team === 100 ? "블루(왼쪽 아래)" : "레드(오른쪽 위)"} · 테두리 <span style="color:var(--mm-me)">금색 나</span> · <span style="color:var(--mm-ally)">파랑 아군</span> · <span style="color:var(--mm-enemy)">빨강 상대</span></figcaption>
    <ul class="lanes">${lane("top", "탑")}${lane("mid", "미드")}${lane("bot", "봇")}</ul>
  </figure>`;
}
