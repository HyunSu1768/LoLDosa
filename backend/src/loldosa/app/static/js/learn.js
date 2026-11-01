/* 배우기: 실력 지도(채점 체크) → 개념 사전 → 개념 한 장.
 * L1 플레이어가 쓰는 말 · L2 개념 하나 + 내 경기 기록 · L3 다음 화면이 예상되는 버튼 · L4 먼저 보여 주고 나중에 묻기 */
import { $, $$, api, badge, empty, ensureLearn, esc, go, linkify, openSheet, post, put, row, skeleton, state, toast } from "./core.js";

export async function renderLearn(view) {
  view.innerHTML = `<div class="page">${skeleton(3)}</div>`;
  const [idx, h, g] = await Promise.all([ensureLearn(true), api("/api/home").catch(() => null), api("/api/gap").catch(() => null)]);
  const skills = (h?.skills || []).filter((s) => s.total);
  // 지금 고칠 것(홈 1순위)과 이어진 개념만 먼저: 사전 전체보다 지금 필요한 것부터 (L2)
  const top = g?.ready ? g.gaps?.[0] : null;
  const now = top ? [top.concept, ...(state.concepts[top.concept]?.related || [])].filter((id, i, a) => state.concepts[id] && a.indexOf(id) === i).slice(0, 4) : [];
  view.innerHTML = `<div class="page">
    <div class="top"><h1>배우기</h1><p>복기에서 나온 개념을 내 경기 기록과 같이 봐요.</p></div>
    ${now.length ? `<h2 class="section">지금 고칠 것과 이어진 개념<small>${esc(top.label)}</small></h2>
      <div class="list">${now.map((id, i) => { const c = state.concepts[id]; const qn = c.quiz_n || 0;
        return row({ title: esc(c.title), sub: esc(c.summary || ""), end: i === 0 ? badge("1순위", "blue") : qn ? `<div class="sub">${qn}문제</div>` : "", href: `#/learn/${id}` }); }).join("")}</div>` : ""}
    ${skills.length ? `<h2 class="section">내 실력 지도<small>경기 기록으로 채점한 것만</small></h2>
      <div class="list">${skills.map((s) => {
        const r = s.pass / s.total;
        return row({ title: esc(s.title), sub: `최근 ${s.total}판 중 ${s.pass}번 지켰어요${s.total < 5 ? " · 판이 적어서 참고만 해요" : ""}`,
          end: `<div class="mini-bar"><i style="width:${Math.max(4, Math.round(r * 100))}%" class="${r >= 0.7 ? "g" : r >= 0.4 ? "y" : "r"}"></i></div>`, href: `#/learn/${s.id}` });
      }).join("")}</div>` : ""}
    ${idx.recommended.length ? `<h2 class="section">다시 볼 개념<small>내 복기에서 자주 나왔어요</small></h2>
      <div class="list">${idx.recommended.map((r) => row({ title: esc(r.title), end: `<div class="sub">${r.count}판</div>`, href: `#/learn/${r.id}` })).join("")}</div>` : ""}
    <h2 class="section">개념 사전</h2>
    <input class="input" id="q" placeholder="찾을 말을 입력해 보세요 (예: 바위게, 턴, 핑)" aria-label="개념 찾기">
    <div id="cats" style="margin-top:16px"></div></div>`;
  const draw = () => {
    const q = $("#q", view).value.trim().replace(/\s/g, "").toLowerCase();
    const match = (c) => !q || [c.title, c.en, c.summary, ...(c.aliases || [])].join(" ").replace(/\s/g, "").toLowerCase().includes(q);
    const html = idx.categories.map((cat) => {
      const items = idx.concepts.filter((c) => c.category === cat.id && match(c));
      if (!items.length) return "";
      return `<div class="eyebrow" style="margin:20px 0 8px">${esc(cat.name)}</div><div class="list">${items.map((c) => {
        const qz = idx.quiz[c.id];
        const done = qz && qz.total && qz.correct / qz.total >= 0.8;
        return row({ title: esc(c.title), sub: esc(c.summary || ""), end: done ? badge("익힘", "green") : c.measurable ? badge("채점", "blue") : "", href: `#/learn/${c.id}` });
      }).join("")}</div>`;
    }).join("");
    $("#cats", view).innerHTML = html || empty({ em: "🔎", title: "찾는 개념이 없어요", desc: "다른 말로 찾아보세요." });
  };
  $("#q", view).oninput = draw;
  draw();
}

export async function renderConcept(view, id) {
  view.innerHTML = `<div class="page">${skeleton(2)}</div>`;
  await ensureLearn();
  let c;
  try { c = await api(`/api/learn/${encodeURIComponent(id)}`); } catch {
    view.innerHTML = `<div class="page">${empty({ title: "이 개념을 찾지 못했어요", action: `<a class="btn grey" href="#/learn">개념 사전으로</a>` })}</div>`;
    return;
  }
  const hist = (c.history || []).filter((x) => x.status !== "na");
  const list = (title, arr, ordered) => (arr && arr.length ? `<h2 class="section">${title}</h2>
    <${ordered ? "ol" : "ul"} class="plain big">${arr.map((x) => `<li>${linkify(x)}</li>`).join("")}</${ordered ? "ol" : "ul"}>` : "");
  view.innerHTML = `<div class="page">
    <a class="back" href="#/learn">← 배우기</a>
    <div class="top"><h1>${esc(c.title)}</h1><p>${esc(c.summary || "")}</p></div>

    ${c.goal ? `<section class="card suggest">
      <div class="eyebrow">내 경기에서는</div>
      <div class="body" style="color:var(--grey900)">${esc(c.goal)}</div>
      ${hist.length ? `<div class="dots" aria-label="최근 경기 기록">${hist.slice().reverse().map((x) =>
        `<span class="d ${x.status}" title="${esc(x.champion || "")} ${esc(x.value)}"></span>`).join("")}</div>
        <div class="sub">최근 ${hist.length}판 중 ${hist.filter((x) => x.status === "pass").length}번 지켰어요 (왼쪽이 오래된 판)</div>`
        : `<div class="sub" style="margin-top:8px">아직 기록이 없어요. 한 판 하면 체크해 드려요.</div>`}
      <div class="btn-row">${c.is_focus ? badge("지금 연습 중이에요", "yellow") : `<button class="btn fill m" id="focus">연습 목표로 정하기</button>`}</div>
    </section>` : ""}

    ${c.validation_note ? `<section class="card" style="margin-top:12px"><div class="eyebrow">실제 경기로 확인한 것</div><p class="body" style="margin:0">${esc(c.validation_note)}</p></section>` : ""}
    ${c.definition ? `<h2 class="section">무엇인가요</h2><p class="body">${linkify(c.definition)}</p>` : ""}
    ${c.why ? `<h2 class="section">왜 중요한가요</h2><p class="body">${linkify(c.why)}</p>` : ""}
    ${list("이렇게 해 보세요", c.how, true)}
    ${list("정글러라면", c.jungler)}
    ${list("자주 하는 실수", c.mistakes)}
    ${(c.quiz || []).length ? `<h2 class="section">이해했는지 확인해요<small>${c.quiz.length}문제</small></h2><div id="quiz"></div>` : ""}
    ${(c.numbers || []).length ? `<h2 class="section">지금 시즌 수치</h2><div class="list">${c.numbers.map((n) => row({ title: esc(n.label), sub: esc(n.note || ""), end: `<div class="val num">${esc(n.value)}</div>` })).join("")}</div>` : ""}
    ${(c.related || []).length ? `<h2 class="section">같이 보면 좋은 개념</h2><div class="list">${c.related.map((r) => row({ title: esc(r.title), href: `#/learn/${r.id}` })).join("")}</div>` : ""}
    ${(c.sources || []).length ? `<details class="fold"><summary>출처 ${c.sources.length}개</summary><ul class="plain">${c.sources.map((s) =>
      `<li>${s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title || s.url)}</a>` : esc(s.title)}${s.note ? ` <span class="sub">${esc(s.note)}</span>` : ""}</li>`).join("")}</ul></details>` : ""}
  </div>`;
  $("#focus", view)?.addEventListener("click", async () => {
    try { await put("/api/focus", { concept: c.id }); toast("연습 목표로 정했어요"); renderConcept(view, id); }
    catch (e) { toast(e.message); }
  });
  if ((c.quiz || []).length) quiz($("#quiz", view), c);
}

/** 퀴즈: 한 번에 한 문제 (One thing per page) */
function quiz(box, c) {
  let i = 0, right = 0;
  const draw = () => {
    if (i >= c.quiz.length) {
      box.innerHTML = `<section class="card"><div class="title" style="font-size:var(--t4)">${c.quiz.length}문제 중 ${right}개 맞혔어요</div>
        <p class="sub">${right === c.quiz.length ? "잘 이해했어요. 다음 판에서 써 봐요." : "틀린 문제는 며칠 뒤 복습에서 다시 나와요."}</p>
        <div class="btn-row"><button class="btn grey m" id="again">다시 풀기</button></div></section>`;
      $("#again", box).onclick = () => { i = 0; right = 0; draw(); };
      return;
    }
    const q = c.quiz[i];
    box.innerHTML = `<section class="card"><div class="eyebrow">${i + 1} / ${c.quiz.length}</div>
      <div class="title" style="font-size:var(--t5);margin-bottom:12px">${esc(q.q)}</div>
      <div class="choices">${q.choices.map((ch, ci) => `<button class="choice" data-c="${ci}">${esc(ch)}</button>`).join("")}</div>
      <div class="reveal"></div></section>`;
    $$(".choice", box).forEach((b) => (b.onclick = async () => {
      const ok = +b.dataset.c === q.answer;
      if (ok) right++;
      $$(".choice", box).forEach((x) => { x.disabled = true; if (+x.dataset.c === q.answer) x.classList.add("right"); else if (x === b) x.classList.add("wrong"); });
      $(".reveal", box).innerHTML = `<div class="verdict ${ok ? "good" : "bad"}">${ok ? "맞았어요" : "아쉬워요"}</div><p class="sub">${esc(q.explain || "")}</p>
        <div class="btn-row end"><button class="btn fill m" id="next">${i + 1 < c.quiz.length ? "다음 문제" : "결과 보기"}</button></div>`;
      $("#next", box).onclick = () => { i++; draw(); };
      post(`/api/learn/${encodeURIComponent(c.id)}/quiz`, { correct: ok }).catch(() => {});
    }));
  };
  draw();
}
