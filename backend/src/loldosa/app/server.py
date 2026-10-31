"""로컬 브리핑 서버. 챔선 상태를 감시하고 WebSocket 으로 UI 에 브리핑을 밀어준다.

    LCU(또는 녹화 재생) → BriefingEngine(즉시) → UI
                        → AI 코치(느림, 선택) → UI
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..analysis.query import StatsDB
from ..briefing.engine import BriefingEngine
from ..config import load_settings
from ..ddragon import ChampionIndex, load_cached
from ..lcu.champselect import ChampSelectState, Stage

log = logging.getLogger(__name__)
STATIC = Path(__file__).parent / "static"
POS_KO = {"top": "탑", "jungle": "정글", "middle": "미드", "bottom": "원딜", "utility": "서폿", "": ""}


def state_view(state: ChampSelectState, champs: ChampionIndex) -> dict:
    def slot(x, mine=False):
        cid = x.shown_champion
        c = champs.get(cid)
        return {
            "cell": x.cell_id, "position": POS_KO.get(x.position, x.position), "champion_id": cid,
            "name": c.name if c else "", "key": c.key if c else "", "locked": x.locked,
            "hovering": bool(cid) and not x.locked, "me": mine,
            "picking": x.cell_id in state.in_progress_cells,
        }

    return {
        "stage": state.stage.value,
        "timer_phase": state.timer_phase,
        "side": "blue" if state.my_team_id == 100 else "red",
        "allies": [slot(a, a.cell_id == state.local_cell_id) for a in state.allies],
        "enemies": [slot(e) for e in state.enemies],
        "ally_bans": [{"champion_id": b, "key": (champs.get(b).key if champs.get(b) else "")} for b in state.ally_bans],
        "enemy_bans": [{"champion_id": b, "key": (champs.get(b).key if champs.get(b) else "")} for b in state.enemy_bans],
    }


class Hub:
    def __init__(self) -> None:
        self.clients: set[WebSocket] = set()
        self.last: dict[str, dict] = {}

    async def send(self, msg: dict) -> None:
        self.last[msg["type"]] = msg
        data = json.dumps(msg, ensure_ascii=False, default=str)
        for ws in list(self.clients):
            try:
                await ws.send_text(data)
            except Exception:
                self.clients.discard(ws)


def create_app(replay: Path | None = None, replay_interval: float = 2.0, ai: bool = True) -> FastAPI:
    settings = load_settings()
    champs = load_cached(settings.data_dir, settings.locale) or ChampionIndex("", {})
    stats = StatsDB(settings.data_dir / "stats.duckdb")
    engine = BriefingEngine(stats, champs)
    hub = Hub()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        task = asyncio.create_task(watcher())
        yield
        task.cancel()

    app = FastAPI(title="LoLDosa", lifespan=lifespan)
    app.state.hub = hub

    coach = None
    if ai:
        from ..coach.claude import ClaudeCoach
        coach = ClaudeCoach()
    ai_task: asyncio.Task | None = None

    async def run_ai(briefing: dict, key: tuple) -> None:
        await hub.send({"type": "ai", "status": "running", "key": str(key)})
        result = await coach.coach(briefing)
        await hub.send({"type": "ai", "key": str(key), **result})

    async def on_state(state: ChampSelectState | None) -> None:
        nonlocal ai_task
        if state is None:
            await hub.send({"type": "idle"})
            return
        briefing = await asyncio.to_thread(engine.build, state)
        b = briefing.to_dict()
        await hub.send({"type": "briefing", "state": state_view(state, champs), "briefing": b,
                        "ddragon": champs.version})
        # AI 는 비용·시간이 들어서 의미 있는 시점에만: 내 픽 확정 직후, 전원 확정
        if coach and state.stage in (Stage.POST_MY_PICK, Stage.FINAL) and b["cards"]:
            key = (state.stage.value, b["my_champion"], b["enemy_jungler"],
                   tuple(sorted(x.champion_id for x in state.enemies if x.locked)))
            if hub.last.get("ai", {}).get("key") != str(key):
                if ai_task and not ai_task.done():
                    ai_task.cancel()
                ai_task = asyncio.create_task(run_ai(b, key))

    async def watcher() -> None:
        if replay:
            from ..lcu.replay import replay as replay_source
            # 데모: 한 번 재생하고 마지막(확정) 화면에서 멈춘다
            async for st in replay_source(replay, interval=replay_interval):
                if st is not None:
                    await on_state(st)
        else:
            from ..lcu.client import watch_champ_select
            async for st in watch_champ_select():
                await on_state(st)

    @app.get("/")
    async def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/api/status")
    async def status():
        from ..lcu.connection import find_credentials
        meta = {}
        if stats.available:
            with stats.session():
                meta = stats.meta()
        return {
            "lcu": find_credentials() is not None or replay is not None,
            "replay": str(replay) if replay else None,
            "stats": meta,
            "ddragon": champs.version,
            "ai": coach.describe() if coach else {"enabled": False},
        }

    @app.websocket("/ws")
    async def ws(sock: WebSocket):
        await sock.accept()
        hub.clients.add(sock)
        for msg in hub.last.values():
            await sock.send_text(json.dumps(msg, ensure_ascii=False, default=str))
        try:
            while True:
                await sock.receive_text()
        except WebSocketDisconnect:
            hub.clients.discard(sock)

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app
