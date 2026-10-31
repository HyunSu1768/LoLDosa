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
                        "ddragon": champs.version,
                        "focus": concept_brief(user.focus_concept) if user.focus_concept else None})
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

    # ---- 개념 학습 -----------------------------------------------------------

    from ..learn.library import Progress, load_library

    library = load_library()
    by_id = {c["id"]: c for c in library.get("concepts", [])}
    progress = Progress(settings.data_dir)

    @app.get("/api/learn")
    async def learn_index():
        from ..learn.skills import CHECKS

        items = [{**{k: c.get(k) for k in ("id", "category", "title", "en", "level", "summary", "aliases")},
                  "measurable": c["id"] in CHECKS}
                 for c in library.get("concepts", [])]
        return {"version": library.get("version", ""), "categories": library.get("categories", []),
                "concepts": items, "read": progress.data["read"], "quiz": progress.data["quiz"],
                "recommended": progress.recommended(library)}

    @app.get("/api/learn/{cid}")
    async def learn_concept(cid: str):
        c = by_id.get(cid)
        if not c:
            raise HTTPException(404, "없는 개념입니다")
        progress.mark_read(cid)
        related = [{"id": r, "title": by_id[r]["title"]} for r in c.get("related", []) if r in by_id]
        from ..learn.skills import CHECKS

        hist = [{"date": h["date"], "champion": h["champion"],
                 "status": h["checks"][0]["status"] if h["checks"] else "na",
                 "value": h["checks"][0]["value"] if h["checks"] else ""} for h in progress.history(cid, 10)]
        return {**c, "related": related, "quiz_progress": progress.data["quiz"].get(cid),
                "flagged": len(progress.data["flags"].get(cid, [])),
                "goal": CHECKS[cid][0] if cid in CHECKS else None, "history": [h for h in hist if h["status"] != "na"],
                "is_focus": user.focus_concept == cid}

    @app.post("/api/learn/{cid}/quiz")
    async def learn_quiz(cid: str, body: dict = Body(...)):
        if cid not in by_id:
            raise HTTPException(404, "없는 개념입니다")
        progress.record_quiz(cid, bool(body.get("correct")))
        return progress.data["quiz"][cid]

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
                        games = list_matches(st, puuid, 30)
            # 새로 받은 경기는 바로 분석해서 성장 기록(개념 체크)을 채운다
            for g in games:
                if g["match_id"] not in progress.data["checks"] and g["position"] == "JUNGLE":
                    try:
                        async with personal_lock:
                            await asyncio.to_thread(_review, g["match_id"])
                    except Exception:  # noqa: BLE001
                        log.exception("auto review failed %s", g["match_id"])
            return annotate(games)
        except ValueError as e:
            raise HTTPException(400, str(e))
        except RiotApiError as e:
            raise HTTPException(502, "Riot 이 키를 거부했습니다 (.env 의 RIOT_API_KEY 확인)" if e.status in (401, 403)
                                else str(e))

    def annotate(games: list[dict]) -> list[dict]:
        for g in games:
            rec = progress.data["checks"].get(g["match_id"])
            checks = rec["checks"] if rec else []
            g["fails"] = [c["concept"] for c in checks if c["status"] == "fail"]
            focus = next((c for c in checks if c["concept"] == user.focus_concept), None)
            g["focus_status"] = focus["status"] if focus else None
        return games

    @app.get("/api/review/matches")
    async def review_matches():
        from ..review.sync import list_matches

        if not user.puuid:
            return []
        async with personal_lock:
            with personal_store() as st:
                return annotate(list_matches(st, user.puuid, 30))

    def _review(match_id: str) -> dict:
        from ..review.analyze import Reviewer

        with personal_store() as st:
            rv = Reviewer(st, stats, champs).review(match_id, user.puuid).to_dict()
        # 리뷰에서 지적된 개념은 '추천 학습'으로 쌓고, 개념 체크는 성장 기록으로 남긴다
        progress.flag({c for l in rv["lessons"] for c in l["concepts"] if c in by_id}, match_id)
        progress.record_checks(match_id, rv["summary"], rv["checks"])
        for c in rv["checks"]:
            c["title"] = by_id.get(c["concept"], {}).get("title", c["concept"])
            c["focus"] = c["concept"] == user.focus_concept
        for l in rv["lessons"] + rv["strengths"]:
            l["concepts"] = [{"id": c, "title": by_id[c]["title"]} for c in l["concepts"] if c in by_id]
        rv["key_lesson"] = key_lesson(rv)
        return rv

    def key_lesson(rv: dict) -> dict | None:
        """이 경기에서 하나만 배운다면: 연습 목표 개념의 실패 > 가장 심각한 피드백."""
        focus_fail = next((c for c in rv["checks"] if c["focus"] and c["status"] == "fail"), None)
        pick = None
        if focus_fail:
            pick = next((l for l in rv["lessons"] if any(x["id"] == focus_fail["concept"] for x in l["concepts"])), None)
        pick = pick or (rv["lessons"][0] if rv["lessons"] else None)
        if not pick or not pick["concepts"]:
            return None
        cid = (focus_fail or {}).get("concept") or pick["concepts"][0]["id"]
        c = by_id.get(cid)
        if not c:
            return None
        return {"lesson": pick, "concept": {k: c.get(k) for k in ("id", "title", "summary", "definition", "how")}}

    def concept_brief(cid: str) -> dict | None:
        c = by_id.get(cid)
        if not c:
            return None
        from ..learn.skills import CHECKS
        return {"id": cid, "title": c["title"], "summary": c.get("summary"), "how": (c.get("how") or [])[:3],
                "goal": CHECKS[cid][0] if cid in CHECKS else None}

    @app.get("/api/home")
    async def home():
        from ..learn.skills import CHECKS

        rates = progress.skill_rates(10)
        skills = []
        for cid, (goal, _) in CHECKS.items():
            r = rates.get(cid, {"pass": 0, "total": 0})
            skills.append({"id": cid, "title": by_id.get(cid, {}).get("title", cid), "goal": goal,
                           "pass": r["pass"], "total": r["total"]})
        measured = [x for x in skills if x["total"] >= 3]
        suggest = min(measured, key=lambda x: x["pass"] / x["total"]) if measured else None
        focus = None
        if user.focus_concept:
            focus = {**(concept_brief(user.focus_concept) or {"id": user.focus_concept}),
                     "history": [{"date": h["date"], "champion": h["champion"],
                                  "status": h["checks"][0]["status"] if h["checks"] else "na",
                                  "value": h["checks"][0]["value"] if h["checks"] else ""}
                                 for h in progress.history(user.focus_concept, 10)]}
        return {"riot_id": user.riot_id, "onboarded": user.onboarded, "pool": len(user.champion_pool),
                "focus": focus, "skills": sorted(skills, key=lambda x: (x["total"] == 0, x["pass"] / max(x["total"], 1))),
                "suggest": suggest, "recommended": progress.recommended(library),
                "games_tracked": len(progress.data["checks"]), "stats_ready": stats.available}

    @app.put("/api/focus")
    async def set_focus(body: dict = Body(...)):
        from ..learn.skills import CHECKS

        cid = body.get("concept", "")
        if cid and cid not in CHECKS:
            raise HTTPException(400, "측정할 수 있는 개념만 연습 목표로 정할 수 있어요")
        user.update({"focus_concept": cid, "onboarded": True}).save(settings.data_dir)
        return {"focus": concept_brief(cid) if cid else None}

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
