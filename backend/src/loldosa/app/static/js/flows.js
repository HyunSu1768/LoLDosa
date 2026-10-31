/* 여러 화면에서 쓰는 흐름: 오늘의 복습(간격 반복), 게임 끝 알림. */
import { $, $$, api, esc, go, linkify, openSheet, closeSheet, post } from "./core.js";
import { board } from "./review.js";

/* ---------- 오늘의 복습: 한 문제씩 ---------- */
export async function startSrs(after) {
  const r = await api("/api/srs/due");
  const items = r.items || [];
  let i = 0, right = 0;
  const sh = openSheet("", { wide: true, onClose: after });
  const draw = () => {
    if (i >= items.length) {
      sh.innerHTML = `<button class="close" aria-label="닫기" data-close>✕</button><h2>오늘 복습을 끝냈어요</h2>
        <p class="body">${items.length}개 중 ${right}개를 맞혔어요. 틀린 건 내일, 맞힌 건 간격을 늘려서 다시 나와요.</p>
        <div class="btn-row end"><button class="btn fill m" data-close>닫기</button></div>`;
      return;
    }
    const it = items[i];
    const head = `<button class="close" aria-label="닫기" data-close>✕</button><div class="eyebrow">복습 ${i + 1} / ${items.length}</div>`;
    const done = async (ok, html) => {
      if (ok) right++;
      await post("/api/srs/grade", { key: it.key, correct: ok }).catch(() => {});
      $(".reveal", sh).innerHTML = `${html}<div class="btn-row end"><button class="btn fill m" id="nx">${i + 1 < items.length ? "다음" : "결과 보기"}</button></div>`;
      $("#nx", sh).onclick = () => { i++; draw(); };
    };
    if (it.kind === "quiz") {
      sh.innerHTML = `${head}<h2>${esc(it.concept.title)}</h2><div class="title" style="margin:8px 0 12px">${esc(it.q)}</div>
        <div class="choices">${it.choices.map((c, ci) => `<button class="choice" data-c="${ci}">${esc(c)}</button>`).join("")}</div><div class="reveal"></div>`;
      $$(".choice", sh).forEach((b) => (b.onclick = () => {
        const ok = +b.dataset.c === it.answer;
        $$(".choice", sh).forEach((x) => { x.disabled = true; if (+x.dataset.c === it.answer) x.classList.add("right"); else if (x === b) x.classList.add("wrong"); });
        done(ok, `<div class="verdict ${ok ? "good" : "bad"}">${ok ? "맞았어요" : "아쉬워요"}</div><p class="sub">${esc(it.explain)}</p>`);
      }));
    } else {
      const mo = it.moment;
      sh.innerHTML = `${head}<h2 class="num">${mo.minute}:00 · ${esc(mo.reason)}</h2>
        <div class="mo-grid">${board(mo.snapshot, 260)}<div><ul class="plain">${mo.snapshot.facts.map((f) => `<li>${linkify(f)}</li>`).join("")}</ul>
        <div class="title" style="margin:12px 0 8px">여기서 뭐 할래요?</div>
        <div class="choices">${mo.choices.map((c) => `<button class="choice" data-a="${c.action}">${esc(c.label)}</button>`).join("")}</div>
        <div class="reveal"></div></div></div>`;
      $$(".choice", sh).forEach((b) => (b.onclick = () => {
        const ok = mo.good.includes(b.dataset.a);
        $$(".choice", sh).forEach((x) => { x.disabled = true; if (mo.good.includes(x.dataset.a)) x.classList.add("right"); else if (x === b) x.classList.add("wrong"); });
        done(ok, `<div class="verdict ${ok ? "good" : "bad"}">${ok ? "좋아요" : "다시 볼 장면이에요"}</div><p class="sub">${esc(mo.verdict)}</p>`);
      }));
    }
  };
  draw();
}

/* ---------- 게임이 끝나면: 이번 판 핵심 하나 (방해하지 않게 오른쪽 아래에 띄움) ---------- */
export function onPostgame(msg) {
  const seen = `pg:${msg.match_id}:${msg.status}`;
  if (msg.match_id && localStorage.getItem(seen)) return;
  let box = $("#postgame");
  if (!box) { box = Object.assign(document.createElement("aside"), { id: "postgame" }); box.setAttribute("aria-live", "polite"); document.body.appendChild(box); }
  const close = `<button class="close" aria-label="닫기" data-pg-close>✕</button>`;
  if (msg.status !== "ready") {
    box.innerHTML = `<div class="pg">${close}<div class="title">${esc(msg.message)}</div></div>`;
  } else {
    box.innerHTML = `<div class="pg">${close}
      <div class="eyebrow">방금 판 · ${esc(msg.champion || "")} ${msg.win ? "승리" : "패배"}</div>
      <div class="title" style="font-size:var(--t5)">${msg.lesson?.title ? esc(msg.lesson.title) : "눈에 띄는 큰 실수는 없었어요"}</div>
      ${msg.focus ? `<div class="sub" style="margin-top:6px">연습 목표 ${esc(msg.focus.title)} · ${msg.focus.status === "pass" ? "지켰어요" : "놓쳤어요"}</div>` : ""}
      ${msg.gap ? `<div class="sub">챌린저와 차이: ${esc(msg.gap.label)} ${esc(msg.gap.mine_text)}</div>` : ""}
      <div class="btn-row"><button class="btn fill m" data-pg-open>복기 보기</button></div></div>`;
    try { if (window.Notification?.permission === "granted") new Notification("방금 판 복기가 준비됐어요", { body: msg.lesson?.title || "" }); } catch {}
  }
  box.onclick = (e) => {
    if (e.target.closest("[data-pg-close]")) { localStorage.setItem(seen, "1"); box.innerHTML = ""; }
    if (e.target.closest("[data-pg-open]")) { localStorage.setItem(seen, "1"); box.innerHTML = ""; go(`#/review/${msg.match_id}`); }
  };
}
