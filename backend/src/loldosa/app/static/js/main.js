/* 시작점: 내비, 라우트, 실시간 연결.
 * Context-based: 챔피언 선택이 시작되면 어느 화면에 있든 브리핑으로 넘어간다 (사용자가 찾아갈 필요 없게). */
import { $, api, esc, go, openSheet, render, route, state } from "./core.js";
import { renderHome } from "./home.js";
import { hasLiveBriefing, onBriefingMessage, renderBrief } from "./brief.js";
import { renderReview, renderReviewList } from "./review.js";
import { renderConcept, renderLearn } from "./learn.js";
import { renderSettings } from "./settings.js";
import { checkClaudeOnStart, checkUpdateOnStart, onPostgame } from "./flows.js";

route(/^#\/home$/, renderHome);
route(/^#\/brief$/, renderBrief);
route(/^#\/review$/, renderReviewList);
route(/^#\/review\/([\w-]+)$/, renderReview);
route(/^#\/learn$/, renderLearn);
route(/^#\/learn\/([\w-]+)$/, renderConcept);
route(/^#\/settings$/, renderSettings);

document.body.classList.toggle("show-ev", localStorage.getItem("showEv") === "1");

async function status() {
  try {
    const s = await api("/api/status");
    state.status = s; state.ddragon = s.ddragon || state.ddragon;
    $("#conn").className = `conn ${s.lcu || s.replay ? "on" : ""}`;
    $("#conn span").textContent = s.replay ? "데모 재생 중" : s.lcu ? "롤과 연결됐어요" : "롤이 꺼져 있어요";
    if (s.window_error && !sessionStorage.getItem("winNote")) { sessionStorage.setItem("winNote", "1"); windowNote(s.window_error); }
  } catch { /* 서버 재시작 중 */ }
}

/* 앱 창 대신 브라우저로 열렸을 때: 조용히 넘어가지 않고 이유와 해결법을 한 번 알려 준다 */
function windowNote(why) {
  const wv2 = why.includes("WebView2");
  openSheet(`<h2>앱 창 대신 브라우저로 열었어요</h2>
    <p class="body">${esc(why)}.</p>
    <p class="body">${wv2 ? "Microsoft 공식 사이트에서 'WebView2 런타임'을 설치하고 앱을 다시 켜면 창으로 열려요. 기능은 브라우저에서도 똑같이 쓸 수 있어요."
      : "기능은 브라우저에서도 똑같이 쓸 수 있어요. 설정 > 진단 기록을 보내 주시면 고칠게요."}</p>
    <div class="btn-row end">${wv2 ? `<a class="btn weak m" href="https://developer.microsoft.com/microsoft-edge/webview2/" target="_blank" rel="noopener">WebView2 받기</a>` : ""}
      <button class="btn fill m" data-close>확인</button></div>`);
}

let wasLive = false;
function connect() {
  const ws = new WebSocket(`ws://${location.host}/ws`);
  ws.onclose = () => setTimeout(connect, 1500);
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (["briefing", "ai", "ended"].includes(msg.type)) {
      onBriefingMessage(msg);
      const live = hasLiveBriefing();
      $("#brief-dot").classList.toggle("hidden", !live);
      if (live && !wasLive && !location.hash.startsWith("#/brief")) go("#/brief");
      wasLive = live;
    } else if (msg.type === "postgame") onPostgame(msg);
  };
}

await status();
connect();
setInterval(status, 15000);
if (!location.hash) location.hash = "#/home";
render();
setTimeout(checkClaudeOnStart, 1500);
setTimeout(checkUpdateOnStart, 2500);
if (window.Notification?.permission === "default") { try { Notification.requestPermission(); } catch {} }
