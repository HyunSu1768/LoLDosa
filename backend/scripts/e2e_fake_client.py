"""실제 롤 클라이언트 없이 앱 전체 흐름 검증: 가짜 LCU(HTTPS + 기본 인증 + lockfile)를 띄우고 앱을 일반 모드로 실행한다.

흐름: lockfile 발견 → 챔선 세션(녹화본) 단계별 진행 → 브리핑 메시지 → 게임 시작(InProgress) → 종료(EndOfGame)
     → 자동 복기 알림(postgame ready) → 진단 기록 zip 에 챔선·게임 단계 기록이 남았는지.

사용: python scripts/e2e_fake_client.py <data_dir(개인 경기·통계 있는 곳)> <game_id(개인 DB에 있는 경기 번호)>
성공하면 0, 실패하면 1 로 끝난다.
"""
import asyncio
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import httpx
import uvicorn
import websockets
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples" / "champselect_ranked_jungle.jsonl"
PASSWORD = "fakepass"


def fake_lcu(game_id: int) -> tuple[FastAPI, dict]:
    sessions = [json.loads(line) for line in SAMPLE.read_text(encoding="utf-8").splitlines() if line.strip()]
    state = {"i": 0, "phase": "ChampSelect", "t0": time.time(), "calls": 0}
    app = FastAPI()

    @app.middleware("http")
    async def auth(request: Request, call_next):
        import base64

        want = "Basic " + base64.b64encode(f"riot:{PASSWORD}".encode()).decode()
        if request.headers.get("authorization") != want:
            return JSONResponse({"message": "unauthorized"}, 401)
        state["calls"] += 1
        return await call_next(request)

    def advance():
        # 챔선 녹화본을 1.2초마다 한 단계씩, 끝나면 게임 시작 → 6초 뒤 종료
        el = time.time() - state["t0"]
        state["i"] = min(int(el / 1.2), len(sessions))
        if state["i"] >= len(sessions):
            state["phase"] = "InProgress" if el < len(sessions) * 1.2 + 6 else "EndOfGame"

    @app.get("/lol-champ-select/v1/session")
    async def session():
        advance()
        if state["phase"] != "ChampSelect":
            return JSONResponse({"message": "not in champ select"}, 404)
        s = sessions[min(state["i"], len(sessions) - 1)]
        return s if s is not None else JSONResponse({}, 404)

    @app.get("/lol-gameflow/v1/gameflow-phase")
    async def phase():
        advance()
        return state["phase"]

    @app.get("/lol-gameflow/v1/session")
    async def gf_session():
        return {"phase": state["phase"], "gameData": {"gameId": game_id, "queue": {"id": 420}}}

    @app.get("/lol-summoner/v1/current-summoner")
    async def summoner():
        return {"gameName": "fake", "tagLine": "KR1"}

    return app, state


async def main() -> int:
    src_data, game_id = Path(sys.argv[1]), int(sys.argv[2])
    work = Path(tempfile.mkdtemp(prefix="loldosa_e2e_"))
    data = work / "data"
    shutil.copytree(src_data, data, ignore=shutil.ignore_patterns("diagnostics", "*.wal"))
    # 자체 서명 인증서 (실제 LCU 도 Riot 자체 서명 인증서를 쓴다)
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-subj", "/CN=127.0.0.1",
                    "-keyout", str(work / "k.pem"), "-out", str(work / "c.pem")], check=True, capture_output=True)
    lport, aport = 29999, 28796
    (work / "lockfile").write_text(f"LeagueClient:1234:{lport}:{PASSWORD}:https")

    lcu_app, lstate = fake_lcu(game_id)
    lcu = uvicorn.Server(uvicorn.Config(lcu_app, host="127.0.0.1", port=lport, log_level="warning",
                                        ssl_keyfile=str(work / "k.pem"), ssl_certfile=str(work / "c.pem")))
    lcu_task = asyncio.create_task(lcu.serve())

    env = {**os.environ, "LOLDOSA_DATA_DIR": str(data), "LOLDOSA_LOCKFILE": str(work / "lockfile")}
    app = subprocess.Popen([sys.executable, "-m", "loldosa.cli", "app", "--browser", "--no-ai", "--port", str(aport)],
                           env=env, cwd=ROOT, stdout=open(work / "app.log", "w"), stderr=subprocess.STDOUT)
    got = {"stages": [], "postgame": None, "errors": []}
    try:
        async with httpx.AsyncClient() as http:
            for _ in range(60):
                try:
                    if (await http.get(f"http://127.0.0.1:{aport}/api/status")).status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                await asyncio.sleep(0.5)
        lstate["t0"] = time.time()  # 앱이 뜬 뒤부터 챔선 시작
        async with websockets.connect(f"ws://127.0.0.1:{aport}/ws") as ws:
            deadline = time.time() + 60
            while time.time() < deadline and not (got["postgame"] and got["postgame"].get("status") == "ready"):
                try:
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=2))
                except asyncio.TimeoutError:
                    continue
                if msg["type"] == "briefing":
                    st = msg["briefing"]["stage"]
                    if not got["stages"] or got["stages"][-1] != st:
                        got["stages"].append(st)
                elif msg["type"] == "postgame":
                    got["postgame"] = msg
                elif msg["type"] == "error":
                    got["errors"].append(msg)
        async with httpx.AsyncClient() as http:
            z = zipfile.ZipFile(io.BytesIO((await http.get(f"http://127.0.0.1:{aport}/api/diagnostics")).content))
            got["diagnostics"] = z.namelist()
    finally:
        app.terminate()
        app.wait(10)
        lcu.should_exit = True
        await lcu_task
    pg = got["postgame"] or {}
    checks = {
        "챔선 단계별 브리핑": len(got["stages"]) >= 3,
        "최종 단계 도달": bool(got["stages"]) and got["stages"][-1] == "final",
        "게임 종료 → 자동 복기 알림": pg.get("status") == "ready",
        "알림에 핵심/챌린저 차이": bool(pg.get("lesson") or pg.get("gap")),
        "진단 기록(챔선)": any(n.startswith("champselect_") for n in got.get("diagnostics", [])),
        "진단 기록(게임 단계)": any(n.startswith("gameflow_") for n in got.get("diagnostics", [])),
        "오류 메시지 없음": not got["errors"],
    }
    print(json.dumps({"stages": got["stages"], "postgame": {k: pg.get(k) for k in ("status", "match_id", "champion")},
                      "lesson": (pg.get("lesson") or {}).get("title"), "gap": (pg.get("gap") or {}).get("label"),
                      "diagnostics": got.get("diagnostics"), "lcu_calls": lstate["calls"]}, ensure_ascii=False, indent=1))
    for k, v in checks.items():
        print(("✅ " if v else "❌ ") + k)
    if not all(checks.values()):
        print((work / "app.log").read_text()[-3000:])
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
