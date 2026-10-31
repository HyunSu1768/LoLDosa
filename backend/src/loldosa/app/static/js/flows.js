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
        <div class="mo-grid">${board(mo.snapshot, 340)}<div><ul class="plain">${mo.snapshot.facts.filter((f) => !f.startsWith("라인:")).map((f) => `<li>${linkify(f)}</li>`).join("")}</ul>
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

/* ---------- Claude 준비: 설치(공식 스크립트) → 로그인(공식 창) ----------
 * 토큰은 앱이 다루지 않는다. 로그인은 Claude 의 공식 브라우저 로그인으로 사용자가 직접 한다. */
import { api as _api, post as _post, toast as _toast } from "./core.js";

export async function claudeSetupSheet({ reason = "", after } = {}) {
  let st = await _api("/api/claude").catch(() => ({ installed: false }));
  const sh = openSheet("", { onClose: after });
  const draw = () => {
    const step = !st.installed ? "install" : !st.logged_in ? "login" : "done";
    sh.innerHTML = `<button class="close" aria-label="닫기" data-close>✕</button>
      <div class="eyebrow">AI 코치 준비</div>
      <h2>${step === "install" ? "Claude를 먼저 설치할게요" : step === "login" ? "Claude에 로그인해 주세요" : "AI 코치를 쓸 수 있어요"}</h2>
      ${reason ? `<p class="sub">${esc(reason)}</p>` : ""}
      <ol class="steps3">
        <li class="${st.installed ? "done" : "on"}">Claude 설치 <span class="sub">Anthropic 공식 설치 스크립트로 설치해요</span></li>
        <li class="${st.logged_in ? "done" : st.installed ? "on" : ""}">Claude 로그인 <span class="sub">새 창에서 브라우저가 열려요. 쓰고 있는 Claude 구독 계정으로 로그인해요</span></li>
        <li class="${st.logged_in ? "done" : ""}">AI 코치 사용</li>
      </ol>
      <p class="sub" id="cl-msg">${step === "done" ? "브리핑과 복기에서 AI 코치 정리를 볼 수 있어요." : "LoLDosa는 로그인 정보를 보거나 저장하지 않아요. 로그인은 Claude가 직접 처리해요."}</p>
      <div class="btn-row end">
        ${step === "done" ? `<button class="btn fill m" data-close>다 됐어요</button>` : `<button class="btn grey m" data-close>다음에</button>`}
        ${step === "install" ? `<button class="btn fill m" id="cl-go">Claude 설치하기</button>` : ""}
        ${step === "login" ? `<button class="btn fill m" id="cl-go">Claude 로그인하기</button>` : ""}
      </div>`;
    $("#cl-go", sh)?.addEventListener("click", step === "install" ? doInstall : doLogin);
  };
  const doInstall = async () => {
    $("#cl-go", sh).disabled = true;
    $("#cl-msg", sh).textContent = "설치하는 중이에요. 1~2분 걸려요.";
    const r = await _post("/api/claude/install").catch((e) => ({ ok: false, log: e.message }));
    st = { ...st, ...r };
    if (!r.ok) { draw(); $("#cl-msg", sh).innerHTML = `<span class="bad">설치하지 못했어요.</span> 인터넷 연결을 확인하고 다시 눌러 주세요.`; return; }
    _toast("Claude를 설치했어요"); draw();
  };
  const doLogin = async () => {
    const r = await _post("/api/claude/login").catch((e) => ({ ok: false, message: e.message }));
    $("#cl-msg", sh).textContent = r.message || "";
    if (!r.ok) return;
    $("#cl-go", sh).disabled = true;
    for (let i = 0; i < 60 && document.body.contains(sh); i++) {  // 3분 동안 3초마다 로그인됐는지 확인
      await new Promise((ok) => setTimeout(ok, 3000));
      st = await _api("/api/claude").catch(() => st);
      if (st.logged_in) { _toast("Claude에 로그인했어요"); draw(); return; }
    }
    if (document.body.contains(sh)) { $("#cl-go", sh).disabled = false; $("#cl-msg", sh).textContent = "아직 로그인이 안 됐어요. 열린 창에서 로그인을 끝낸 뒤 다시 눌러 주세요."; }
  };
  draw();
}

/** 앱을 켤 때: AI 코치가 켜져 있는데 준비가 안 됐으면 하루에 한 번만 묻는다 (매번 묻지 않게). */
export async function checkClaudeOnStart() {
  const st = await _api("/api/claude").catch(() => null);
  if (!st || !st.ai_enabled || (st.installed && st.logged_in)) return;
  const last = +localStorage.getItem("claudeAskedAt") || 0;
  if (Date.now() - last < 24 * 3600 * 1000) return;
  localStorage.setItem("claudeAskedAt", String(Date.now()));
  claudeSetupSheet({ reason: "AI 코치가 켜져 있는데 Claude가 준비되지 않았어요. 설정에서 AI 코치를 끄면 다시 묻지 않아요." });
}
