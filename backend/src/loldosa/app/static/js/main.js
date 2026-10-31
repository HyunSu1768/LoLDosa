/* 시작점: 내비, 라우트, 실시간 연결.
 * Context-based: 챔피언 선택이 시작되면 어느 화면에 있든 브리핑으로 넘어간다 (사용자가 찾아갈 필요 없게). */
import { $, api, go, render, route, state } from "./core.js";
import { renderHome } from "./home.js";
import { hasLiveBriefing, onBriefingMessage, renderBrief } from "./brief.js";
import { renderReview, renderReviewList } from "./review.js";
import { renderConcept, renderLearn } from "./learn.js";
import { renderSettings } from "./settings.js";
import { checkClaudeOnStart, onPostgame } from "./flows.js";

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
  } catch { /* 서버 재시작 중 */ }
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
if (window.Notification?.permission === "default") { try { Notification.requestPermission(); } catch {} }
