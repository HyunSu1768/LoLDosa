/* 설정: 꼭 필요한 것만, 바꾸면 바로 저장 (저장 버튼 없음).
 * S1 없으면 목표를 못 이루는 것만 · S2 에러는 상황→원인→고치는 버튼 · S3 보조 버튼은 「닫기」 · S5 키보드로 모두 조작 */
import { $, $$, api, champImg, ensureChamps, esc, openSheet, put, row, skeleton, state, toast } from "./core.js";
import { claudeSetupSheet, updateSheet } from "./flows.js";

export async function renderSettings(view) {
  view.innerHTML = `<div class="page">${skeleton(2)}</div>`;
  await ensureChamps();
  const [s, key, st, cl, up] = await Promise.all([api("/api/settings"), api("/api/riot-key").catch(() => ({})), api("/api/status").catch(() => ({})),
    api("/api/claude").catch(() => ({})), api("/api/update").catch(() => ({}))]);
  const keyOk = key.set && !key.problem;
  view.innerHTML = `<div class="page">
    <div class="top"><h1>설정</h1></div>
    <div class="list">
      ${row({ lead: st.lcu && !st.replay ? "🟢" : "⚪", title: st.replay ? "데모 재생 중이에요" : st.lcu ? "롤 클라이언트와 연결됐어요" : "롤 클라이언트가 꺼져 있어요",
        sub: st.lcu ? "챔피언 선택·게임 종료를 자동으로 알아채요" : "롤을 켜면 자동으로 연결돼요" })}
      ${row({ lead: "🔑", title: "Riot API 키", sub: keyOk ? `넣었어요 · ${esc(key.masked)}` : "없어도 돼요. 넣으면 핑 같은 지표까지 볼 수 있어요", attrs: 'data-act="key"' })}
      ${row({ lead: "🧩", title: "내 챔프폭", sub: s.champion_pool?.length ? `${s.champion_pool.length}명 · 추천 픽을 이 안에서 골라요` : "고르면 추천 픽을 이 안에서 골라요", attrs: 'data-act="pool"' })}
    </div>

    <h2 class="section">비교 기준</h2>
    <div class="list">
      <div class="row"><div class="mid"><div class="title">갱 추천에 쓸 티어</div><div class="sub">상대 반응에 따라 달라지는 건 내 티어 기록을 먼저 써요</div></div>
        <div class="seg" data-key="my_bucket">${seg([["platinum", "플래티넘"], ["apex", "마스터+"]], s.my_bucket)}</div></div>
      <div class="row"><div class="mid"><div class="title">따라잡을 다음 티어</div><div class="sub">복기 비교표의 '다음 티어'에 쓰여요</div></div>
        <div class="seg" data-key="target_bucket">${seg([["emerald", "에메랄드"], ["diamond", "다이아"], ["apex", "마스터+"]], s.target_bucket)}</div></div>
    </div>

    <h2 class="section">보기</h2>
    <div class="list">
      <label class="row"><div class="mid"><div class="title">AI 코치</div><div class="sub">Claude 구독으로 브리핑·복기를 한 번 더 정리해요 (10~20초)</div></div>
        <input type="checkbox" class="toggle" data-key="ai_enabled" ${s.ai_enabled ? "checked" : ""}></label>
      ${row({ lead: cl.logged_in ? "✅" : "🤖", title: !cl.installed ? "Claude가 설치돼 있지 않아요" : !cl.logged_in ? "Claude 로그인이 필요해요" : "Claude에 로그인돼 있어요",
        sub: !cl.installed ? "눌러서 공식 설치 스크립트로 설치해요" : !cl.logged_in ? "눌러서 Claude 로그인 창을 열어요" : `로그인 방식: ${cl.auth_method === "claude.ai" ? "Claude 구독" : esc(cl.auth_method || "")}`,
        attrs: 'data-act="claude"' })}
      <label class="row"><div class="mid"><div class="title">근거 판 수 보기</div><div class="sub">문장마다 몇 판을 보고 말했는지 작게 보여 줘요</div></div>
        <input type="checkbox" class="toggle" id="ev" ${document.body.classList.contains("show-ev") ? "checked" : ""}></label>
    </div>

    <h2 class="section">버전</h2>
    <div class="list">
      ${row({ lead: up.available ? "⬆️" : "✅", title: up.available ? `${esc(up.latest)}로 업데이트할 수 있어요` : `최신 버전이에요 · ${esc(up.current || "")}`,
        sub: up.available ? (up.can_apply ? "눌러서 바로 업데이트해요" : "소스로 실행 중이라 git pull 로 업데이트해 주세요") : (up.error ? esc(up.error) : "새 버전이 나오면 켤 때 알려 드려요"),
        ...(up.available && up.can_apply ? { attrs: 'data-act="update"' } : {}) })}
    </div>

    <h2 class="section">문제가 생겼을 때</h2>
    <div class="list">
      ${row({ lead: "🧾", title: "진단 기록 내려받기", sub: "롤 클라이언트 응답과 게임 단계 기록이 들어 있어요. 비밀번호·API 키는 없어요", href: "/api/diagnostics" })}
    </div>
    <p class="sub" style="margin-top:24px">${st.stats?.built_at ? `고티어 데이터 · ${esc(st.stats.built_at.slice(0, 10))} 기준 · 패치 ${esc(st.stats.latest_patch || "")}` : ""}</p>
  </div>`;

  // 바꾸면 바로 저장: 저장 버튼을 누르는 일을 없앤다
  $$(".seg", view).forEach((g) => g.addEventListener("click", async (e) => {
    const b = e.target.closest("button"); if (!b) return;
    $$("button", g).forEach((x) => x.classList.toggle("on", x === b));
    await put("/api/settings", { [g.dataset.key]: b.dataset.v }); toast("바꿨어요");
  }));
  $$('input[data-key]', view).forEach((t) => (t.onchange = async () => { await put("/api/settings", { [t.dataset.key]: t.checked }); toast(t.checked ? "켰어요" : "껐어요"); }));
  $("#ev", view).onchange = (e) => { document.body.classList.toggle("show-ev", e.target.checked); localStorage.setItem("showEv", e.target.checked ? "1" : "0"); };
  view.addEventListener("click", (e) => {
    const a = e.target.closest("[data-act]")?.dataset.act;
    if (a === "key") keySheet(() => renderSettings(view));
    if (a === "pool") poolSheet(s.champion_pool || [], () => renderSettings(view));
    if (a === "claude") claudeSetupSheet({ after: () => renderSettings(view) });
    if (a === "update") updateSheet(up);
  });
}
const seg = (opts, cur) => opts.map(([v, l]) => `<button type="button" data-v="${v}" class="${v === cur ? "on" : ""}">${l}</button>`).join("");

function keySheet(after) {
  const sh = openSheet(`<h2>Riot API 키 넣기</h2>
    <p class="body">developer.riotgames.com에 롤 계정으로 로그인하면 바로 받을 수 있어요. 개발용 키는 24시간마다 바뀌어요.</p>
    <div class="field"><label for="k">API 키</label><input class="input" id="k" placeholder="RGAPI-로 시작해요" autocomplete="off"></div>
    <p class="sub" id="kmsg"></p>
    <div class="btn-row end"><button class="btn grey m" data-close>닫기</button><button class="btn fill m" id="save">확인하고 저장하기</button></div>`);
  $("#save", sh).onclick = async () => {
    $("#kmsg", sh).textContent = "Riot에 확인하는 중이에요";
    try { await put("/api/riot-key", { key: $("#k", sh).value }); toast("키를 저장했어요"); after(); }
    catch (e) { $("#kmsg", sh).innerHTML = `<span class="bad">${esc(e.message)}</span> 키를 다시 복사해서 넣어 주세요.`; }
  };
}

function poolSheet(cur, after) {
  const pool = new Set(cur);
  const sh = openSheet(`<h2>내 챔프폭 고르기</h2><p class="sub">자주 하는 정글 챔피언을 골라 주세요. 추천 픽이 이 안에서 나와요.</p>
    <input class="input" id="cq" placeholder="챔피언 찾기" style="margin:12px 0">
    <div class="champ-grid" id="cg"></div>
    <div class="btn-row end"><button class="btn grey m" data-close>닫기</button><button class="btn fill m" id="save">${pool.size}명 저장하기</button></div>`, { wide: true });
  const draw = () => {
    const q = $("#cq", sh).value.trim().replace(/\s/g, "").toLowerCase();
    const list = state.champList.filter((c) => !q || c.name.replace(/\s/g, "").toLowerCase().includes(q))
      .sort((a, b) => (b.jungle_games || 0) - (a.jungle_games || 0));
    $("#cg", sh).innerHTML = list.map((c) => `<button class="champ ${pool.has(c.id) ? "on" : ""}" data-id="${c.id}" aria-pressed="${pool.has(c.id)}">${champImg(c.key)}<span>${esc(c.name)}</span></button>`).join("");
  };
  $("#cq", sh).oninput = draw;
  $("#cg", sh).onclick = (e) => {
    const b = e.target.closest(".champ"); if (!b) return;
    const id = +b.dataset.id; pool.has(id) ? pool.delete(id) : pool.add(id);
    b.classList.toggle("on"); b.setAttribute("aria-pressed", pool.has(id));
    $("#save", sh).textContent = `${pool.size}명 저장하기`;
  };
  $("#save", sh).onclick = async () => { await put("/api/settings", { champion_pool: [...pool] }); toast("챔프폭을 저장했어요"); after(); };
  draw();
}
