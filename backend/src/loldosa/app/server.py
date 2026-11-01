"""로컬 브리핑 서버. 챔선 상태를 감시하고 WebSocket 으로 UI 에 브리핑을 밀어준다.

    LCU(또는 녹화 재생) → BriefingEngine(즉시) → UI
                        → AI 코치(느림, 선택) → UI
"""

from __future__ import annotations

import asyncio
import os
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
            raise HTTPException(409, "다른 프로그램(터미널의 loldosa review 등)이 경기 DB를 쓰는 중이에요. 잠시 후 다시 시도하세요.")
        try:
            yield store
        finally:
            store.close()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        tasks = [asyncio.create_task(watcher())]
        if not replay:
            tasks.append(asyncio.create_task(postgame_watcher()))
        yield
        for t in tasks:
            t.cancel()

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
                        "focus": concept_brief(user.focus_concept) if user.focus_concept else None,
                        "practice": await asyncio.to_thread(top_practice),
                        "my_champs": gap_cache.get("champs", {})})
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
            await hub.send({"type": "error", "message": "챔피언 선택 감시 중 오류가 났어요. 터미널 로그를 확인하세요."})

    DIAG = settings.data_dir / "diagnostics"

    async def postgame_watcher() -> None:
        """게임이 끝나면 경기를 받아 바로 복기하고, 핵심 하나를 화면에 띄운다."""
        from ..lcu.postgame import watch_game_end

        try:
            async for ev in watch_game_end(log_dir=DIAG):
                if ev["type"] == "start":
                    asyncio.create_task(record_live(ev["game_id"]))
                else:
                    asyncio.create_task(postgame(ev["game_id"]))
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("게임 종료 감시 중 오류")

    LIVE_DIR = settings.data_dir / "livegame"
    live_tasks: dict[int, asyncio.Task] = {}

    async def record_live(game_id: int) -> None:
        """게임 중 초 단위 기록 (Live Client Data API). 화면에는 아무것도 띄우지 않는다."""
        from ..lcu.livegame import record

        task = asyncio.current_task()
        live_tasks[game_id] = task
        try:
            path = await record(LIVE_DIR, game_id, url=os.getenv("LOLDOSA_LIVE_URL", "https://127.0.0.1:2999/liveclientdata/allgamedata"))
            log.info("live record %s → %s", game_id, path)
        except Exception:
            log.exception("게임 중 기록 실패")

    async def postgame(game_id: int, tries: int = 20, wait_s: float = 30.0) -> dict | None:
        t = live_tasks.pop(game_id, None)
        if t and not t.done():  # 기록이 파일로 저장될 때까지 잠깐 기다린다
            try:
                await asyncio.wait_for(asyncio.shield(t), timeout=15)
            except asyncio.TimeoutError:
                pass
        from ..riot.client import RiotClient

        mid = f"{settings.platform.upper()}_{game_id}"
        if user.puuid:  # 이미 받아 둔 경기면 API 없이 바로 복기
            async with personal_lock:
                with personal_store() as st:
                    have = st.has_match(mid)
                if have:
                    msg = postgame_message(await asyncio.to_thread(_review, mid), mid)
            if have:
                await hub.send(msg)
                return msg
        if not settings.riot_api_key:  # 키가 없으면 롤 클라이언트 전적에서 바로 받는다
            msg = await postgame_from_lcu(game_id, mid)
            if msg:
                return msg
        if not settings.riot_api_key or not user.puuid:
            await hub.send({"type": "postgame", "status": "need_setup",
                            "message": "게임이 끝났어요. 자동 복기를 하려면 경기 복기 탭에서 Riot ID를 한 번 불러와 주세요."})
            return None
        mid = f"{settings.platform.upper()}_{game_id}"
        await hub.send({"type": "postgame", "status": "waiting", "match_id": mid,
                        "message": "게임 끝! Riot 서버에 경기 기록이 올라오면 바로 복기할게요 (보통 1~3분)."})
        async with RiotClient(settings.riot_api_key, settings.platform, settings.region) as riot:
            for _ in range(tries):
                match = await riot.match(mid)
                timeline = await riot.timeline(mid) if match else None
                if match and timeline:
                    async with personal_lock:
                        with personal_store() as st:
                            if not st.has_match(mid):
                                st.save_raw(mid, match, timeline)
                                st.ingest(match, timeline, "personal")
                        rv = await asyncio.to_thread(_review, mid)
                    msg = postgame_message(rv, mid)
                    await hub.send(msg)
                    return msg
                await asyncio.sleep(wait_s)
        await hub.send({"type": "postgame", "status": "timeout", "match_id": mid,
                        "message": "경기 기록이 아직 안 올라왔어요. 조금 뒤 경기 복기 탭에서 불러와 주세요."})
        return None

    async def lcu_me() -> dict:
        """켜져 있는 롤 클라이언트의 내 계정 {puuid, gameName, tagLine} (없으면 빈 dict)."""
        from ..lcu.client import LcuClient
        from ..lcu.connection import find_credentials

        creds = find_credentials()
        if not creds:
            return {}
        lcu = LcuClient(creds)
        try:
            return await lcu.current_summoner() or {}
        except Exception:  # noqa: BLE001
            return {}
        finally:
            await lcu.aclose()

    async def lcu_store_games(game_ids: list[int]) -> list[str]:
        """롤 클라이언트 전적 → 개인 경기 DB (키 없이). 내 puuid 도 클라이언트에서 채운다."""
        from ..lcu.client import LcuClient
        from ..lcu.connection import find_credentials
        from ..lcu.matchhistory import fetch

        creds = find_credentials()
        if not creds:
            raise HTTPException(409, "롤 클라이언트가 켜져 있어야 키 없이 전적을 불러올 수 있어요.")
        lcu = LcuClient(creds)
        saved = []
        try:
            me = await lcu.current_summoner() or {}
            if me.get("puuid") and me["puuid"] != user.puuid:
                rid = f"{me.get('gameName', '')}#{me.get('tagLine', '')}".strip("#")
                user.update({"puuid": me["puuid"], "riot_id": user.riot_id or rid}).save(settings.data_dir)
            for gid in game_ids:
                mid = f"{settings.platform.upper()}_{gid}"
                with personal_store() as st:
                    if st.has_match(mid):
                        saved.append(mid)
                        continue
                got = await fetch(lcu, gid, settings.platform, DIAG)
                if not got:
                    continue
                with personal_store() as st:
                    st.save_raw(mid, *got)
                    st.ingest(got[0], got[1], "personal")
                saved.append(mid)
        finally:
            await lcu.aclose()
        return saved

    async def postgame_from_lcu(game_id: int, mid: str) -> dict | None:
        for _ in range(10):  # 게임 직후엔 클라이언트 전적에 바로 안 뜰 수 있다
            try:
                async with personal_lock:
                    saved = await lcu_store_games([game_id])
                if saved:
                    async with personal_lock:
                        msg = postgame_message(await asyncio.to_thread(_review, mid), mid)
                    await hub.send(msg)
                    return msg
            except HTTPException:
                return None
            except Exception:
                log.exception("클라이언트 전적 가져오기 실패")
            await asyncio.sleep(15)
        return None

    @app.post("/api/review/sync-lcu")
    async def review_sync_lcu(body: dict = Body(default={})):
        """키 없이 내 최근 솔랭을 롤 클라이언트에서 불러오기."""
        from ..lcu.client import LcuClient
        from ..lcu.connection import find_credentials
        from ..lcu.matchhistory import recent_game_ids
        from ..review.sync import list_matches

        creds = find_credentials()
        if not creds:
            raise HTTPException(409, "롤 클라이언트가 켜져 있어야 키 없이 전적을 불러올 수 있어요.")
        lcu = LcuClient(creds)
        try:
            ids = await recent_game_ids(lcu, int(body.get("count", 20)))
        except Exception as e:  # noqa: BLE001
            log.exception("lcu history failed")
            from ..lcu.postgame import diag_write
            diag_write(DIAG, "errors", {"where": "lcu_history", "error": f"{type(e).__name__}: {e}"})
            raise HTTPException(502, f"롤 클라이언트 전적을 읽지 못했어요. ({type(e).__name__}: {str(e)[:160]})")
        finally:
            await lcu.aclose()
        if not ids:
            raise HTTPException(404, "롤 클라이언트 전적에 최근 협곡 게임이 없어요.")
        async with personal_lock:
            await lcu_store_games(ids)
            with personal_store() as st:
                games = list_matches(st, user.puuid, 30)
        for g in games:
            if g["match_id"] not in progress.data["checks"] and g["position"] == "JUNGLE":
                try:
                    async with personal_lock:
                        await asyncio.to_thread(_review, g["match_id"])
                except Exception:  # noqa: BLE001
                    log.exception("auto review failed %s", g["match_id"])
        return annotate(games)

    def postgame_message(rv: dict, mid: str) -> dict:
        """복기 결과에서 '이번 판 핵심 하나'와 연습 목표 결과, 가장 아쉬운 실력 지표 하나."""
        sm = rv["summary"]
        kl = rv.get("key_lesson") or {}
        lesson = (kl.get("lesson") or {}) if kl else {}
        focus = next((c for c in rv["checks"] if c.get("focus") and c["status"] != "na"), None)
        worst = next((g for g in rv.get("gap", []) if not g["ok"]), None)
        return {"type": "postgame", "status": "ready", "match_id": mid, "champion": sm.get("champion"),
                "win": sm.get("win"), "is_jungle": rv.get("is_jungle"),
                "lesson": {"title": lesson.get("title"), "text": lesson.get("text")} if lesson else None,
                "focus": {"title": focus["title"], "status": focus["status"], "value": focus["value"]} if focus else None,
                "gap": worst,
                "live": (rv.get("live") or {}).get("text")}

    @app.post("/api/postgame/test")
    async def postgame_test(body: dict = Body(...)):
        """게임 없이 자동 복기 흐름을 확인: 이미 받은 경기 id 로 알림을 띄운다."""
        mid = body.get("match_id", "")
        async with personal_lock:
            rv = await asyncio.to_thread(_review, mid)
        msg = postgame_message(rv, mid)
        await hub.send(msg)
        return msg

    @app.get("/api/update")
    async def update_check():
        """GitHub Releases 최신 버전과 비교."""
        from ..updater import check

        return await asyncio.to_thread(check)

    @app.post("/api/update/apply")
    async def update_apply():
        """내려받고 → 압축 풀고 → 앱을 끈 뒤 파일을 바꾸고 다시 켠다."""
        from ..updater import apply, check, frozen

        if not frozen():
            raise HTTPException(400, "소스로 실행 중이에요. 저장소에서 git pull 로 업데이트해 주세요.")
        info = await asyncio.to_thread(check)
        if not info.get("available"):
            raise HTTPException(400, "이미 최신 버전이에요.")

        def bye():
            import threading

            threading.Timer(1.5, lambda: os._exit(0)).start()  # 진행 상황 응답이 나간 뒤 종료

        apply(info, bye)
        return {"ok": True, "latest": info["latest"]}

    @app.get("/api/update/progress")
    async def update_progress():
        from ..updater import progress

        return progress

    @app.get("/api/claude")
    async def claude_status():
        """AI 코치 준비 상태: 설치됐는지, 로그인됐는지 (토큰은 다루지 않고 `claude auth status` 결과만)."""
        from ..coach.setup import status as claude_st

        return {**await asyncio.to_thread(claude_st), "ai_enabled": user.ai_enabled}

    @app.post("/api/claude/install")
    async def claude_install():
        """Anthropic 공식 설치 스크립트 실행."""
        from ..coach.setup import install

        return await asyncio.to_thread(install)

    @app.post("/api/claude/login")
    async def claude_login():
        """새 창에서 공식 로그인(`claude auth login`)을 띄운다. 사용자가 브라우저에서 직접 로그인한다."""
        from ..coach.setup import open_login

        return await asyncio.to_thread(open_login)

    @app.get("/api/riot-key")
    async def riot_key_status():
        from ..config import key_problem

        k = settings.riot_api_key
        return {"set": bool(k), "problem": key_problem(k) if k else "키가 없어요",
                "masked": f"{k[:10]}…{k[-4:]}" if k else None}

    @app.put("/api/riot-key")
    async def riot_key_save(body: dict = Body(...)):
        """설정 화면에서 키 입력 → 형식 확인 → 실제로 Riot에 한 번 물어보고 → .env 에 저장."""
        from ..config import clean_key, key_problem, save_api_key
        from ..riot.client import RiotApiError, RiotClient

        key = clean_key(body.get("key", ""))
        if problem := key_problem(key):
            raise HTTPException(400, problem)
        try:
            async with RiotClient(key, settings.platform, settings.region) as riot:
                await riot.apex_league("challenger")
        except RiotApiError as e:
            raise HTTPException(400, "Riot이 이 키를 거부했어요. 개발용 키는 24시간마다 만료돼요." if e.status in (401, 403)
                                else f"Riot 응답 오류: {e}")
        save_api_key(key, settings.env_path)
        object.__setattr__(settings, "riot_api_key", key)
        return {"ok": True, "masked": f"{key[:10]}…{key[-4:]}"}

    @app.get("/api/diagnostics")
    async def diagnostics():
        """진단 기록 묶음(zip): 실제 클라이언트에서 문제가 생기면 이 파일 하나를 보내 주면 돼요."""
        import io
        import zipfile

        from fastapi.responses import Response

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(DIAG.glob("*.jsonl")) if DIAG.exists() else []:
                z.write(f, f.name)
            log_file = settings.data_dir / "loldosa.log"
            if log_file.exists():
                z.write(log_file, "loldosa.log")
        return Response(buf.getvalue(), media_type="application/zip",
                        headers={"Content-Disposition": "attachment; filename=loldosa_diagnostics.zip"})

    async def _watch() -> None:
        if replay:
            from ..lcu.replay import replay as replay_source
            # 데모: 한 번 재생하고 마지막(확정) 화면에서 멈춘다
            async for st in replay_source(replay, interval=replay_interval):
                if st is not None:
                    await on_state(st)
        else:
            from ..lcu.client import watch_champ_select
            async for st in watch_champ_select(log_dir=DIAG):
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
        from . import desktop

        return {
            "window_error": desktop.window_error,
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
        from ..learn.skills import CHECKS, GRADED

        items = [{**{k: c.get(k) for k in ("id", "category", "title", "en", "level", "summary", "aliases", "related")},
                  "measurable": c["id"] in GRADED, "quiz_n": len(c.get("quiz") or [])}
                 for c in library.get("concepts", [])]
        return {"version": library.get("version", ""), "categories": library.get("categories", []),
                "concepts": items, "read": progress.data["read"], "quiz": progress.data["quiz"],
                "recommended": progress.recommended(library)}

    @app.get("/api/learn/{cid}")
    async def learn_concept(cid: str):
        c = by_id.get(cid)
        if not c:
            raise HTTPException(404, "없는 개념이에요")
        progress.mark_read(cid)
        related = [{"id": r, "title": by_id[r]["title"]} for r in c.get("related", []) if r in by_id]
        from ..learn.skills import CHECKS, GRADED

        hist = [{"date": h["date"], "champion": h["champion"],
                 "status": h["checks"][0]["status"] if h["checks"] else "na",
                 "value": h["checks"][0]["value"] if h["checks"] else ""} for h in progress.history(cid, 10)]
        return {**c, "related": related, "quiz_progress": progress.data["quiz"].get(cid),
                "flagged": len(progress.data["flags"].get(cid, [])),
                "goal": CHECKS[cid][0] if cid in CHECKS else None, "history": [h for h in hist if h["status"] != "na"],
                "is_focus": user.focus_concept == cid, "mastery": progress.mastery(cid)}

    @app.post("/api/learn/{cid}/quiz")
    async def learn_quiz(cid: str, body: dict = Body(...)):
        if cid not in by_id:
            raise HTTPException(404, "없는 개념이에요")
        progress.record_quiz(cid, bool(body.get("correct")))
        return progress.data["quiz"][cid]

    # ---- 경기 리뷰 -----------------------------------------------------------

    def review_ready():
        if not settings.riot_api_key:
            raise HTTPException(400, "RIOT_API_KEY가 없어요 (.env)")

    @app.post("/api/review/sync")
    async def review_sync(body: dict = Body(default={})):
        from ..review.sync import list_matches, resolve_puuid, sync_personal
        from ..riot.client import RiotApiError, RiotClient

        review_ready()
        riot_id = (body.get("riot_id") or user.riot_id or "").strip()
        if not riot_id:  # Riot ID 를 따로 묻지 않는다: 켜져 있는 롤 클라이언트의 내 계정
            me = await lcu_me()
            if me.get("puuid"):
                riot_id = f"{me.get('gameName', '')}#{me.get('tagLine', '')}"
                user.update({"riot_id": riot_id, "puuid": me["puuid"]}).save(settings.data_dir)
        if not riot_id:
            raise HTTPException(400, "내 계정을 찾지 못했어요. 롤 클라이언트를 켠 뒤 다시 눌러 주세요.")
        try:
            async with personal_lock:
                async with RiotClient(settings.riot_api_key, settings.platform, settings.region) as riot:
                    puuid = user.puuid if (user.riot_id == riot_id and user.puuid) else await resolve_puuid(riot, riot_id)
                    user.update({"riot_id": riot_id, "puuid": puuid}).save(settings.data_dir)
                    try:
                        solo = next((e for e in await riot.rank_by_puuid(puuid)
                                     if e.get("queueType") == "RANKED_SOLO_5x5"), None)
                        if solo:
                            progress.record_rank(solo)
                    except RiotApiError:
                        pass
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
            raise HTTPException(502, "Riot이 키를 거부했어요. 설정에서 키를 다시 넣어 주세요." if e.status in (401, 403)
                                else f"Riot 서버 응답이 이상해요 ({e})")
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001 — 네트워크·인증서(PC방 보안 프로그램 등) 문제를 사용자에게 그대로 보여 준다
            log.exception("review sync failed")
            from ..lcu.postgame import diag_write
            diag_write(DIAG, "errors", {"where": "review_sync", "error": f"{type(e).__name__}: {e}"})
            raise HTTPException(502, net_error_say(e))

    def net_error_say(e: Exception) -> str:
        t = f"{type(e).__name__}: {e}"
        if "CERTIFICATE" in t.upper() or "SSL" in t.upper():
            return f"보안 연결(인증서) 확인에 실패했어요. PC방 보안 프로그램이 인터넷 연결을 가로채고 있을 수 있어요. ({t[:160]})"
        if "Connect" in type(e).__name__ or "Timeout" in type(e).__name__:
            return f"Riot 서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요. ({t[:160]})"
        return f"경기를 가져오다 문제가 생겼어요. ({t[:200]})"

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

    def personal_features(limit: int = 30) -> list[dict]:
        """최근 정글 판들의 챌린저 갭 지표 (오래된 판 → 최근 판 순)."""
        from ..analysis.gap import jungler_features
        from ..review.sync import list_matches

        rows = []
        with personal_store() as st:
            for m in list_matches(st, user.puuid, limit):
                if m["position"] != "JUNGLE":
                    continue
                raw = st.load_raw(m["match_id"])
                f = jungler_features(raw[0], raw[1], user.puuid) if raw else None
                if f:
                    rows.append({**f, "match_id": m["match_id"], "game_start": m["game_start"]})
        return list(reversed(rows))

    gap_cache: dict = {}

    def top_practice() -> dict | None:
        """밴픽 화면용: 챌린저와 가장 큰 차이 하나 (10분 캐시, 새 경기 복기 때 비움)."""
        import time as _t

        from ..analysis.gap import load_reference, personal_gap

        if gap_cache.get("t", 0) > _t.time() - 600:
            return gap_cache.get("v")
        v = None
        ref = load_reference()
        if ref and user.puuid:
            try:
                rows = personal_features(20)
                if len(rows) >= 3:
                    g = personal_gap(rows, ref, "challenger", limit=1)
                    v = g["gaps"][0] if g["gaps"] else None
                    by: dict = {}
                    for r in rows:
                        by.setdefault(r["champion_id"], []).append(r)
                    gap_cache["champs"] = {str(c): {"progress": personal_gap(rs, ref, "challenger", 1)["progress"],
                                                     "games": len(rs), "wins": sum(1 for x in rs if x["win"])}
                                           for c, rs in by.items() if len(rs) >= 3}
            except HTTPException:
                return gap_cache.get("v")
        gap_cache.update(t=_t.time(), v=v)
        return v

    @app.get("/api/gap")
    async def gap():
        """챌린저까지 가장 큰 차이: 고수와 플래티넘을 실제로 가르는 지표만으로 내 최근 판을 진단."""
        return await _gap()

    @app.post("/api/coach/weekly")
    async def coach_weekly():
        """주간 리포트: 차이 지표·채점 체크·판단 훈련을 근거로 Claude 가 이번 주 연습 계획을 짠다."""
        from ..coach.claude import weekly_evidence

        if not coach:
            return {"status": "disabled", "message": "AI 코치가 꺼져 있어요"}
        g = await _gap()
        if not g.get("ready"):
            return {"status": "not_ready", "message": g.get("reason", "")}
        h = await home()
        ev = weekly_evidence(g, h["skills"], progress.decision_summary(7))
        return await coach.weekly(g, ev)

    async def _gap() -> dict:
        from ..analysis.gap import load_reference, personal_gap

        ref = load_reference()
        if not ref or not user.puuid:
            return {"ready": False, "reason": "경기 복기 탭에서 내 경기를 먼저 불러와 주세요." if ref else "기준표가 없어요."}
        async with personal_lock:
            rows = personal_features(30)
        if len(rows) < 3:
            return {"ready": False, "reason": f"정글 판이 {len(rows)}판뿐이에요. 3판 이상 있어야 진단할 수 있어요."}
        res = personal_gap(rows, ref, "challenger", limit=3)
        for x in res["gaps"]:
            for e in x.get("examples", []):
                e["champion"] = champs.name(e["champion_id"])
        # 변화: 앞쪽 절반 vs 최근 절반
        if len(rows) >= 8:
            half = len(rows) // 2
            old, new = personal_gap(rows[:half], ref, "challenger", 99), personal_gap(rows[half:], ref, "challenger", 99)
            res["progress_before"], res["progress_now"] = old["progress"], new["progress"]
            before = {x["key"]: x for x in old["all"]}
            for x in res["gaps"] + res["strengths"]:
                b = before.get(x["key"])
                x["before_text"] = b["mine_text"] if b else None
        # 흐름: 최근 5판씩 묶은 진행도 (오래된 판 → 최근 판)
        res["series"] = [{"progress": personal_gap(rows[max(0, i - 4): i + 1], ref, "challenger", 1)["progress"],
                          "match_id": rows[i]["match_id"], "game_start": rows[i]["game_start"]}
                         for i in range(2, len(rows))]
        # 챔피언별: 같은 지표로 챔피언마다 진행도 (3판 이상)
        by: dict[int, list] = {}
        for r in rows:
            by.setdefault(r["champion_id"], []).append(r)
        res["by_champion"] = sorted(
            [{"champion_id": c, "name": champs.name(c), "key": (champs.get(c).key if champs.get(c) else ""),
              "games": len(rs), "wins": sum(1 for x in rs if x["win"]),
              "progress": personal_gap(rs, ref, "challenger", 1)["progress"]}
             for c, rs in by.items() if len(rs) >= 3], key=lambda x: -(x["progress"] or 0))
        res["groups"] = ref["groups"]
        res["ready"] = True
        return res

    def _review(match_id: str) -> dict:
        from ..review.analyze import Reviewer

        with personal_store() as st:
            rv = Reviewer(st, stats, champs).review(match_id, user.puuid).to_dict()
        # 게임 중 초 단위 기록이 있으면 행동 목표(골드 바로 쓰기·쉬는 시간 없애기)도 채점한다
        from ..lcu.livegame import load as load_live, summarize as live_summary

        rec = load_live(LIVE_DIR, int(match_id.split("_")[-1])) if "_" in match_id else None
        rv["live"] = live_summary(rec) if rec else None
        if rv["live"] and rv["live"].get("samples", 0) > 10 and rv.get("is_jungle"):
            from ..learn.skills import evaluate

            rv["facts"].update(live_rich_s=rv["live"]["rich_s"], live_idle_n=len(rv["live"]["idle"]))
            rv["checks"] = evaluate(rv["facts"])
        # 리뷰에서 지적된 개념은 '추천 학습'으로 쌓고, 개념 체크는 성장 기록으로 남긴다
        progress.flag({c for l in rv["lessons"] for c in l["concepts"] if c in by_id}, match_id)
        progress.record_checks(match_id, rv["summary"], rv["checks"], rv.get("facts"))
        for cid in {c for l in rv["lessons"] for c in l["concepts"] if c in by_id}:
            progress.schedule(f"quiz:{cid}", "quiz", {"concept": cid})
        attach_compare(rv, match_id)
        for c in rv["checks"]:
            c["title"] = by_id.get(c["concept"], {}).get("title", c["concept"])
            c["focus"] = c["concept"] == user.focus_concept
        for l in rv["lessons"] + rv["strengths"]:
            l["concepts"] = [{"id": c, "title": by_id[c]["title"]} for c in l["concepts"] if c in by_id]
        rv["key_lesson"] = key_lesson(rv)
        gap_cache.clear()
        return rv

    METRIC_KEYS = {"3:00까지 먹은 캠프": "camps3", "10분 정글 CS": "cs10", "10분 전 데스": "deaths10",
                   "분당 시야 점수": "vision_pm", "첫 귀환": "first_recall_s"}

    def fmt_metric(key: str, v: float) -> str:
        if key == "first_recall_s":
            return f"{int(v) // 60}:{int(v) % 60:02d}"
        return f"{v:.2f}" if key == "vision_pm" else f"{v:.1f}" if key in ("deaths10", "camps3") else f"{v:.0f}"

    def attach_compare(rv: dict, match_id: str) -> None:
        """비교표에 '다음 티어 평균'과 '내 최근 평균'을 붙인다."""
        base = progress.baseline(exclude=match_id)
        tgt = {}
        if stats.available:
            with stats.session():
                tgt = stats.bucket_avgs(user.target_bucket)
        rv["compare"] = {"target_label": {"emerald": "에메랄드", "diamond": "다이아", "platinum": "플래티넘",
                                          "apex": "마스터+"}.get(user.target_bucket, user.target_bucket),
                         "target_games": tgt.get("games", 0), "me_games": base.get("games", 0)}
        for m in rv["metrics"]:
            k = METRIC_KEYS.get(m["label"])
            if not k:
                continue
            if tgt.get(k) is not None:
                m["target"] = fmt_metric(k, tgt[k])
            if base.get(k) is not None:
                m["me_avg"] = fmt_metric(k, base[k])

    def key_lesson(rv: dict) -> dict | None:
        """이 경기에서 하나만 배운다면: 연습 목표 개념의 실패 > 가장 심각한 피드백."""
        focus_fail = next((c for c in rv["checks"] if c["focus"] and c["status"] == "fail"), None)
        pick = None
        if focus_fail:
            pick = next((l for l in rv["lessons"] if any(x["id"] == focus_fail["concept"] for x in l["concepts"])), None)
        if not pick and rv["lessons"]:
            # 사용자가 '아니에요'를 더 많이 누른 규칙(3번 이상)은 핵심 교훈에서 뒤로 미룬다
            from ..review.analyze import lesson_rule

            st = progress.lesson_rule_stats()
            bad = {k for k, v in st.items() if v["no"] >= 3 and v["no"] > v["ok"]}
            pick = next((l for l in rv["lessons"] if lesson_rule(l["title"]) not in bad), rv["lessons"][0])
        if not pick or not pick["concepts"]:
            return None
        cid = (focus_fail or {}).get("concept") or pick["concepts"][0]["id"]
        c = by_id.get(cid)
        if not c:
            return None
        from ..review.analyze import lesson_rule

        return {"lesson": pick, "rule": lesson_rule(pick["title"]),
                "concept": {k: c.get(k) for k in ("id", "title", "summary", "definition", "how")}}

    def concept_brief(cid: str) -> dict | None:
        c = by_id.get(cid)
        if not c:
            return None
        from ..learn.skills import CHECKS, GRADED, IF_THEN
        return {"id": cid, "title": c["title"], "summary": c.get("summary"), "how": (c.get("how") or [])[:3],
                "goal": CHECKS[cid][0] if cid in CHECKS else None, "graded": cid in GRADED, "if_then": IF_THEN.get(cid)}

    @app.get("/api/home")
    async def home():
        from ..learn.skills import CHECKS, GRADED

        rates = progress.skill_rates(10)
        skills = []
        for cid, (goal, _) in CHECKS.items():
            if cid not in GRADED:
                continue
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
            if user.focus_concept not in GRADED:
                focus["note"] = ("이 목표는 실제 경기 검증에서 프로·챌린저와 플래티넘 사이 차이가 없어서 더 이상 채점하지 않아요. "
                                 "아래에서 다른 연습 목표를 골라 주세요.")
        from ..learn.library import effect_report, rank_label

        for x in skills:
            x["mastery"] = progress.mastery(x["id"])
        return {"riot_id": user.riot_id, "onboarded": user.onboarded, "pool": len(user.champion_pool),
                "due": len(progress.due_items(999)),
                "effect": effect_report(progress, user.focus_concept, user.focus_set_at),
                "rank": rank_label(progress.data["ranks"][-1]) if progress.data["ranks"] else None,
                "practice": top_practice(), "focus": focus, "skills": sorted(skills, key=lambda x: (x["total"] == 0, x["pass"] / max(x["total"], 1))),
                "suggest": suggest, "recommended": progress.recommended(library),
                "games_tracked": len(progress.data["checks"]), "stats_ready": stats.available,
                "ai_ready": bool(coach and coach.enabled and user.ai_enabled)}

    @app.put("/api/focus")
    async def set_focus(body: dict = Body(...)):
        from ..learn.skills import CHECKS, GRADED

        cid = body.get("concept", "")
        if cid and cid not in GRADED:
            raise HTTPException(400, "실제 경기 검증을 통과한 체크가 있는 개념만 연습 목표로 정할 수 있어요")
        from datetime import datetime, timezone

        if cid != user.focus_concept:
            user.update({"focus_set_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        user.update({"focus_concept": cid, "onboarded": True}).save(settings.data_dir)
        return {"focus": concept_brief(cid) if cid else None}

    @app.get("/api/review/{match_id}")
    async def review_match(match_id: str):
        if not user.puuid:
            raise HTTPException(400, "먼저 Riot ID로 경기를 불러오세요")
        try:
            async with personal_lock:
                return await asyncio.to_thread(_review, match_id)
        except KeyError as e:
            raise HTTPException(404, str(e))

    @app.get("/api/review/{match_id}/moments")
    async def review_moments(match_id: str):
        """그 순간으로 돌아가기: 판단 지점 + 비슷한 상황의 고티어 선택."""
        from ..review.moments import build_moments

        if not user.puuid:
            raise HTTPException(400, "먼저 Riot ID로 경기를 불러오세요")

        def work():
            with personal_store() as st, stats.session():
                return build_moments(st.con, stats, champs, match_id, user.puuid)

        async with personal_lock:
            moments = await asyncio.to_thread(work)
        for mo in moments:
            mo["concepts"] = [{"id": c, "title": by_id[c]["title"]} for c in mo["concepts"] if c in by_id]
        return moments

    @app.post("/api/lesson/feedback")
    async def lesson_feedback(body: dict = Body(...)):
        """'이 교훈이 맞나요?' — 교훈 규칙의 정확도를 실제 사용자 판단으로 잰다."""
        progress.record_lesson_feedback(body.get("match_id", ""), body.get("rule", "기타"), bool(body.get("ok")))
        st = progress.lesson_rule_stats().get(body.get("rule", "기타"), {})
        return {"ok": True, "rule_stats": st}

    @app.post("/api/moments/answer")
    async def moment_answer(body: dict = Body(...)):
        progress.record_decision(body.get("match_id", ""), int(body.get("minute", 0)), body.get("choice", ""),
                                 bool(body.get("good")), body.get("concepts") or [], body.get("moment"),
                                 body.get("track_ok"))
        return {"ok": True}

    # ---- 오늘의 복습 -------------------------------------------------------

    @app.get("/api/srs/due")
    async def srs_due():
        items = []
        for it in progress.due_items():
            if it["kind"] == "quiz":
                c = by_id.get(it["ref"]["concept"])
                if not c or not c.get("quiz"):
                    continue
                q = c["quiz"][hash(it["key"] + it["due"]) % len(c["quiz"])]
                items.append({"key": it["key"], "kind": "quiz", "concept": {"id": c["id"], "title": c["title"]},
                              "q": q["q"], "choices": q["choices"], "answer": q["answer"], "explain": q.get("explain", "")})
            else:
                items.append({"key": it["key"], "kind": "moment", "moment": it["ref"]})
        return {"items": items, "total_due": len(progress.due_items(999))}

    @app.post("/api/srs/grade")
    async def srs_grade(body: dict = Body(...)):
        it = progress.grade(body.get("key", ""), bool(body.get("correct")))
        if it and it["kind"] == "quiz":
            progress.record_quiz(it["ref"]["concept"], bool(body.get("correct")))
        return it or {}

    @app.post("/api/replay/{match_id}")
    async def open_replay(match_id: str, body: dict = Body(default={})):
        """롤 클라이언트에서 그 경기 리플레이를 열고 그 시각으로 이동."""
        from ..lcu.game_replay import open_replay_at

        statuses: list[str] = []
        res = await open_replay_at(match_id, float(body.get("t", 0)), on_status=statuses.append)
        return {**res, "log": statuses}

    @app.post("/api/review/{match_id}/ai")
    async def review_ai(match_id: str):
        if not coach:
            return {"status": "disabled", "message": "AI 코치가 꺼져 있어요"}
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
