"""로컬 브리핑 서버. 챔선 상태를 감시하고 WebSocket 으로 UI 에 브리핑을 밀어준다.

    LCU(또는 녹화 재생) → BriefingEngine(즉시) → UI
                        → AI 코치(느림, 선택) → UI
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
import logging
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..analysis.query import StatsDB
from ..briefing.engine import BriefingEngine
from ..config import load_settings
from ..ddragon import ChampionIndex, load_cached
from ..lcu.champselect import ChampSelectState, Stage
from ..review.sync import PERSONAL_DB
from ..settings import UserSettings
from ..store.matches import MatchStore

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
    user = UserSettings.load(settings.data_dir)
    engine = BriefingEngine(stats, champs, settings.data_dir / "guides.duckdb", user)
    hub = Hub()
    personal_lock = asyncio.Lock()

    @contextmanager
    def personal_store():
        """개인 경기 DB 는 요청마다 열고 닫는다 (터미널의 `loldosa review` 와 동시에 써도 되도록)."""
        import duckdb

        try:
            store = MatchStore(settings.data_dir, filename=PERSONAL_DB)
        except duckdb.IOException:
            raise HTTPException(409, "다른 프로그램(터미널의 loldosa review 등)이 경기 DB 를 쓰는 중입니다. 잠시 후 다시 시도하세요.")
        try:
            yield store
        finally:
            store.close()

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
            # 챔선이 끝나도 마지막 브리핑은 남겨둔다 (로딩 화면에서 읽을 수 있게)
            await hub.send({"type": "ended"})
            return
        hub.last.pop("ended", None)
        briefing = await asyncio.to_thread(engine.build, state)
        b = briefing.to_dict()
        await hub.send({"type": "briefing", "state": state_view(state, champs), "briefing": b,
                        "ddragon": champs.version})
        # AI 는 비용·시간이 들어서 의미 있는 시점에만: 내 픽 확정 직후, 전원 확정
        if coach and user.ai_enabled and state.stage in (Stage.POST_MY_PICK, Stage.FINAL) and b["cards"]:
            key = (state.stage.value, b["my_champion"], b["enemy_jungler"],
                   tuple(sorted(x.champion_id for x in state.enemies if x.locked)))
            if hub.last.get("ai", {}).get("key") != str(key):
                if ai_task and not ai_task.done():
                    ai_task.cancel()
                ai_task = asyncio.create_task(run_ai(b, key))

    async def watcher() -> None:
        try:
            await _watch()
        except asyncio.CancelledError:
            raise
        except Exception:  # 감시가 조용히 죽지 않도록
            log.exception("챔선 감시 중 오류")
            await hub.send({"type": "error", "message": "챔피언 선택 감시 중 오류가 났습니다. 터미널 로그를 확인하세요."})

    async def _watch() -> None:
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
            "ai": ({**coach.describe(), "enabled": coach.enabled and user.ai_enabled} if coach
                   else {"enabled": False}),
            "settings": {"riot_id": user.riot_id, "pool": len(user.champion_pool)},
        }

    # ---- 설정 ---------------------------------------------------------------

    @app.get("/api/settings")
    async def get_settings():
        return asdict(user)

    @app.put("/api/settings")
    async def put_settings(patch: dict = Body(...)):
        if "riot_id" in patch and patch["riot_id"] != user.riot_id:
            patch["puuid"] = ""
        user.update(patch).save(settings.data_dir)
        return asdict(user)

    @app.get("/api/champions")
    async def champions():
        jungle = {}
        if stats.available:
            with stats.session():
                s = stats.pick_scope("apex")
                jungle = {r["champion_id"]: r["games"] for r in stats.jungle_pool(s, min_games=1)}
        out = [{"id": c.id, "name": c.name, "key": c.key, "jungle_games": jungle.get(c.id, 0)} for c in champs.all()]
        return sorted(out, key=lambda c: (-c["jungle_games"], c["name"]))

    # ---- 경기 리뷰 -----------------------------------------------------------

    def review_ready():
        if not settings.riot_api_key:
            raise HTTPException(400, "RIOT_API_KEY 가 없습니다 (.env)")

    @app.post("/api/review/sync")
    async def review_sync(body: dict = Body(default={})):
        from ..review.sync import list_matches, resolve_puuid, sync_personal
        from ..riot.client import RiotApiError, RiotClient

        review_ready()
        riot_id = (body.get("riot_id") or user.riot_id).strip()
        if not riot_id:
            raise HTTPException(400, "Riot ID 를 입력하세요 (닉네임#태그)")
        try:
            async with personal_lock:
                async with RiotClient(settings.riot_api_key, settings.platform, settings.region) as riot:
                    puuid = user.puuid if (user.riot_id == riot_id and user.puuid) else await resolve_puuid(riot, riot_id)
                    user.update({"riot_id": riot_id, "puuid": puuid}).save(settings.data_dir)
                    with personal_store() as st:
                        await sync_personal(riot, st, puuid, int(body.get("count", 10)), say=lambda *_: None)
                        return list_matches(st, puuid, 30)
        except ValueError as e:
            raise HTTPException(400, str(e))
        except RiotApiError as e:
            raise HTTPException(502, "Riot 이 키를 거부했습니다 (.env 의 RIOT_API_KEY 확인)" if e.status in (401, 403)
                                else str(e))

    @app.get("/api/review/matches")
    async def review_matches():
        from ..review.sync import list_matches

        if not user.puuid:
            return []
        async with personal_lock:
            with personal_store() as st:
                return list_matches(st, user.puuid, 30)

    def _review(match_id: str) -> dict:
        from ..review.analyze import Reviewer

        with personal_store() as st:
            return Reviewer(st, stats, champs).review(match_id, user.puuid).to_dict()

    @app.get("/api/review/{match_id}")
    async def review_match(match_id: str):
        if not user.puuid:
            raise HTTPException(400, "먼저 Riot ID 로 경기를 불러오세요")
        try:
            async with personal_lock:
                return await asyncio.to_thread(_review, match_id)
        except KeyError as e:
            raise HTTPException(404, str(e))

    @app.post("/api/review/{match_id}/ai")
    async def review_ai(match_id: str):
        if not coach:
            return {"status": "disabled", "message": "AI 코치가 꺼져 있습니다"}
        async with personal_lock:
            rv = await asyncio.to_thread(_review, match_id)
        return await coach.coach_review(rv)

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
