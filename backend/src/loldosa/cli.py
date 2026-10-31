"""loldosa CLI.

    loldosa doctor                 환경 점검 (키, Claude CLI, 롤 클라이언트, 캐시)
    loldosa ddragon sync           최신 패치 챔피언 데이터 받기
    loldosa riot check             Riot API 키 동작 확인 (KR 챌린저 → 경기 1개 타임라인)
    loldosa lcu status             롤 클라이언트 접속 확인
    loldosa lcu watch              챔피언 선택 실시간 감시 (--record 로 녹화)
    loldosa lcu watch --replay F   녹화 파일 재생 (게임 없이 테스트)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

from .config import key_problem, load_settings
from .ddragon import ChampionIndex, load_cached, sync_champions
from .lcu.champselect import ChampSelectState


def _print(msg: str = "") -> None:
    print(msg, flush=True)


# ---- doctor ----------------------------------------------------------------

def cmd_doctor(_args) -> int:
    from .lcu.connection import find_credentials

    s = load_settings()
    ok = True
    _print(f"OS: {sys.platform}")
    _print(f".env 위치: {s.env_path} ({'있음' if s.env_path.exists() else '없음'})")
    if problem := key_problem(s.riot_api_key):
        ok = False
        _print(f"[!!] {problem} → {s.env_path} 에 RIOT_API_KEY=RGAPI-… 를 넣으세요")
    else:
        _print(f"[ok] RIOT_API_KEY 형식 정상 ({s.riot_api_key[:10]}…{s.riot_api_key[-4:]})  "
               f"platform={s.platform} region={s.region}  → 동작 확인: loldosa riot check")

    claude = shutil.which("claude")
    if claude:
        ver = subprocess.run([claude, "--version"], capture_output=True, text=True).stdout.strip()
        _print(f"[ok] Claude Code CLI: {ver}  (구독 로그인 상태는 `claude` 실행으로 확인)")
    else:
        _print("[--] Claude Code CLI 없음 → AI 브리핑 단계(M4) 전까지는 없어도 됨")

    champs = load_cached(s.data_dir, s.locale)
    if champs:
        _print(f"[ok] 챔피언 데이터 캐시: 패치 {champs.version}, {len(champs)}명")
    else:
        _print("[--] 챔피언 데이터 없음 → `loldosa ddragon sync`")

    creds = find_credentials()
    if creds:
        _print(f"[ok] 롤 클라이언트 감지: port {creds.port}")
    else:
        _print("[--] 롤 클라이언트 미실행 (켜져 있는데도 안 잡히면 LOLDOSA_LOCKFILE 로 lockfile 경로 지정)")
    return 0 if ok else 1


# ---- ddragon ---------------------------------------------------------------

def cmd_ddragon_sync(args) -> int:
    s = load_settings()
    idx = asyncio.run(sync_champions(s.data_dir, s.locale, args.version))
    _print(f"패치 {idx.version}: 챔피언 {len(idx)}명 저장 → {s.data_dir / 'ddragon' / idx.version}")
    return 0


# ---- riot ------------------------------------------------------------------

def _key_help(s, status: int) -> None:
    _print(f"[!!] Riot 이 키를 거부했습니다 (HTTP {status}). 사용한 키: {s.riot_api_key[:10]}…{s.riot_api_key[-4:]}")
    _print(f"     - {s.env_path} 의 RIOT_API_KEY 가 developer.riotgames.com 에 보이는 키와 같은지 확인하세요")
    _print("     - 사이트에서 NEW API KEY 를 눌렀다면 이전 키는 즉시 무효가 됩니다")
    _print("     - 개발용 키(DEVELOPMENT API KEY)는 24시간마다 만료됩니다")


def _key_ok(s) -> bool:
    if problem := key_problem(s.riot_api_key):
        _print(f"[!!] {problem} → {s.env_path} 를 확인하세요 (`loldosa doctor`)")
        return False
    return True


async def _riot_check() -> int:
    from .riot.client import RiotApiError, RiotClient

    s = load_settings()
    if not _key_ok(s):
        return 1
    try:
        async with RiotClient(s.riot_api_key, s.platform, s.region) as riot:
            league = await riot.apex_league("challenger")
            entries = league.get("entries", [])
            _print(f"[ok] {s.platform.upper()} 챌린저 {len(entries)}명")
            top = max(entries, key=lambda e: e.get("leaguePoints", 0))
            _print(f"     1위 LP {top['leaguePoints']}, {top['wins']}승 {top['losses']}패")
            ids = await riot.match_ids(top["puuid"], count=1)
            if not ids:
                _print("[--] 최근 솔랭 경기 없음")
                return 0
            tl = await riot.timeline(ids[0])
            frames = tl["info"]["frames"]
            _print(f"[ok] 경기 {ids[0]} 타임라인: {len(frames)}프레임(분), 이벤트 {sum(len(f['events']) for f in frames)}개")
    except RiotApiError as e:
        if e.status in (401, 403):
            _key_help(s, e.status)
        else:
            _print(f"[!!] {e}")
        return 1
    return 0


def cmd_riot_check(_args) -> int:
    return asyncio.run(_riot_check())


# ---- collect --------------------------------------------------------------

async def _collect(args) -> int:
    from .pipeline.collect import CollectConfig, run_collect
    from .riot.client import RiotClient
    from .store.matches import MatchStore

    from .riot.client import RiotApiError

    s = load_settings()
    if not _key_ok(s):
        return 1
    store = MatchStore(s.data_dir)
    try:
        async with RiotClient(s.riot_api_key, s.platform, s.region) as riot:
            for bucket in args.bucket:
                cfg = CollectConfig(bucket=bucket, players=args.players, matches_per_player=args.per_player,
                                    days=args.days, max_matches=args.max_matches, reseed=args.reseed)
                counts = await run_collect(riot, store, cfg, say=_print)
        _print("DB: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    except RiotApiError as e:
        if e.status in (401, 403):
            _key_help(s, e.status)
        else:
            _print(f"[!!] {e}")
        return 1
    finally:
        store.close()
    return 0


def cmd_collect(args) -> int:
    try:
        return asyncio.run(_collect(args))
    except KeyboardInterrupt:
        _print("중단됨 (다시 실행하면 이어서 진행)")
        return 0


# ---- analyze / update / app ------------------------------------------------

def cmd_analyze(_args) -> int:
    from .analysis.build import build_stats

    s = load_settings()
    champs = load_cached(s.data_dir, s.locale)
    if champs is None:
        _print("먼저 `loldosa ddragon sync` 를 실행하세요.")
        return 1
    if not (s.data_dir / "matches.duckdb").exists():
        _print("수집된 경기가 없습니다. 먼저 `loldosa collect`.")
        return 1
    _print("통계 집계 중…")
    counts = build_stats(s.data_dir, champs)
    _print(f"완료 → {s.data_dir / 'stats.duckdb'}")
    _print("  " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    return 0


def cmd_reprocess(_args) -> int:
    from .store.matches import MatchStore

    s = load_settings()
    store = MatchStore(s.data_dir)
    try:
        n = store.reprocess(lambda i, t: _print(f"  {i}/{t}"))
    finally:
        store.close()
    _print(f"원본에서 {n}경기 다시 처리 완료 → `loldosa analyze`")
    return 0


def cmd_update(args) -> int:
    """패치/챔피언 갱신 → 수집 → 분석 (하루 한 번 돌리면 되는 전체 파이프라인)."""
    rc = cmd_ddragon_sync(argparse.Namespace(version=None))
    if rc == 0:
        rc = cmd_collect(args)
    if rc == 0 and not args.skip_pro:
        if cmd_pro_sync(argparse.Namespace(days=90)) != 0:
            _print("(프로 데이터는 건너뜀: 다음 update 때 다시 시도)")
    if rc == 0:
        rc = cmd_analyze(args)
    return rc


def cmd_app(args) -> int:
    from .app.desktop import run

    run(replay=Path(args.replay) if args.replay else None, port=args.port, browser=args.browser,
        ai=not args.no_ai, replay_interval=args.interval)
    return 0


# ---- review ----------------------------------------------------------------

async def _review(args) -> int:
    from .analysis.query import StatsDB
    from .review.analyze import Reviewer
    from .review.sync import PERSONAL_DB, list_matches, resolve_puuid, sync_personal
    from .riot.client import RiotApiError, RiotClient
    from .settings import UserSettings
    from .store.matches import MatchStore

    s = load_settings()
    if not _key_ok(s):
        return 1
    us = UserSettings.load(s.data_dir)
    riot_id = args.riot_id or us.riot_id
    if not riot_id:
        _print("Riot ID 를 입력하세요: loldosa review '닉네임#태그'")
        return 1
    store = MatchStore(s.data_dir, filename=PERSONAL_DB)
    try:
        async with RiotClient(s.riot_api_key, s.platform, s.region) as riot:
            puuid = us.puuid if (us.riot_id == riot_id and us.puuid) else await resolve_puuid(riot, riot_id)
            us.update({"riot_id": riot_id, "puuid": puuid}).save(s.data_dir)
            _print(f"{riot_id} 최근 솔로랭크 {args.count}경기 가져오는 중…")
            await sync_personal(riot, store, puuid, args.count, say=_print)
        games = list_matches(store, puuid, args.count)
        champs = load_cached(s.data_dir, s.locale)
        reviewer = Reviewer(store, StatsDB(s.data_dir / "stats.duckdb"), champs)
        for g in games[: args.show]:
            rv = reviewer.review(g["match_id"], puuid)
            sm = rv.summary
            _print(f"\n■ {sm['date']} {sm['champion']}({sm['position']}) {'승' if sm['win'] else '패'} {sm['kda']} "
                   f"{sm['duration']} vs 정글 {sm['enemy_jungler']}")
            for n in rv.notes:
                _print(f"  · {n}")
            for l in rv.lessons[:3]:
                _print(f"  ✗ {l.title}: {l.text}")
            for l in rv.strengths[:2]:
                _print(f"  ✓ {l.title}")
    except (ValueError, RiotApiError) as e:
        if isinstance(e, RiotApiError) and e.status in (401, 403):
            _key_help(s, e.status)
        else:
            _print(f"[!!] {e}")
        return 1
    finally:
        store.close()
    return 0


def cmd_review(args) -> int:
    return asyncio.run(_review(args))


# ---- ai --------------------------------------------------------------------

def cmd_ai_check(_args) -> int:
    import os
    import time as _time

    from .coach.claude import ClaudeCoach

    coach = ClaudeCoach(timeout=120)
    _print(f"Claude Code CLI: {coach.cli or '없음'}  모델: {coach.model}")
    if os.getenv("ANTHROPIC_API_KEY"):
        _print("[!!] ANTHROPIC_API_KEY 환경변수가 있습니다. 이 경우 구독이 아니라 API 키 과금으로 실행됩니다.")
    if not coach.cli:
        _print("[!!] `claude` 명령을 찾을 수 없습니다. Claude Code 를 설치하세요: https://code.claude.com")
        return 1
    t = _time.time()
    try:
        text = asyncio.run(coach.run_cli('{"ok": true} 라고만 JSON 으로 답해.', system="JSON 한 줄만 출력한다."))
    except Exception as e:  # noqa: BLE001
        _print(f"[!!] 실패: {e}")
        return 1
    _print(f"[ok] 응답 {_time.time() - t:.1f}초: {text.strip()[:80]}")
    return 0


# ---- pro / guides ----------------------------------------------------------

def cmd_pro_sync(args) -> int:
    from .sources.pro import sync_pro

    s = load_settings()
    champs = load_cached(s.data_dir, s.locale)
    if champs is None:
        _print("먼저 `loldosa ddragon sync`.")
        return 1
    try:
        n = asyncio.run(sync_pro(s.data_dir, champs.version, days=args.days, say=_print))
    except RuntimeError as e:
        _print(f"[!!] {e}")
        return 1
    _print(f"프로 정글 기록 {n}건 저장 → `loldosa analyze` 로 통계에 반영")
    return 0


def _name_resolver():
    import re as _re

    s = load_settings()
    champs = load_cached(s.data_dir, s.locale)
    en = {}
    try:
        from .sources.pro import english_names
        en = asyncio.run(english_names(champs.version)) if champs else {}
    except Exception:  # 오프라인이면 한국어/키 매칭만
        pass

    def resolve(name):
        if not name:
            return 0
        key = _re.sub(r"[^a-z0-9]", "", str(name).lower())
        if key in en:
            return en[key]
        c = champs.by_name(str(name)) if champs else None
        return c.id if c else 0
    return resolve


async def _guides_ingest(docs_loader, args) -> int:
    from .coach.claude import ClaudeCoach
    from .sources.guides import GuideKB, extract

    s = load_settings()
    kb = GuideKB(s.data_dir)
    coach = ClaudeCoach(timeout=300)
    if not coach.enabled:
        _print("Claude Code CLI 가 필요합니다 (설치 후 `claude` 로그인).")
        return 1
    resolve = _name_resolver()
    total = 0
    async for doc in docs_loader():
        if doc is None:
            continue
        _print(f"• {doc.title} ({doc.author}) — {len(doc.text)}자")
        claims, dropped = await extract(doc, coach, resolve, say=_print)
        kb.save(doc, claims)
        total += len(claims)
        _print(f"  저장 {len(claims)}개 (원문에서 인용을 찾지 못해 버린 항목 {dropped}개)")
    _print(f"완료: 주장 {total}개")
    return 0


def cmd_guides_add(args) -> int:
    from .sources.guides import load_youtube

    async def loader():
        for url in args.urls:
            try:
                yield await load_youtube(url)
            except Exception as e:  # noqa: BLE001
                _print(f"[!!] {url}: 자막을 가져오지 못했습니다 ({type(e).__name__})")
                yield None
    return asyncio.run(_guides_ingest(loader, args))


def cmd_guides_search(args) -> int:
    from .sources.guides import GuideKB, load_youtube, search_youtube

    async def loader():
        kb = GuideKB(load_settings().data_dir)
        for q in args.query:
            ids = await search_youtube(q, args.max)
            _print(f"검색 '{q}': {len(ids)}개")
            for vid in ids:
                url = f"https://www.youtube.com/watch?v={vid}"
                if kb.has_source(url):
                    continue
                try:
                    yield await load_youtube(url)
                except Exception as e:  # noqa: BLE001
                    _print(f"  [--] {url}: 자막 없음/차단 ({type(e).__name__})")
    return asyncio.run(_guides_ingest(loader, args))


def cmd_guides_text(args) -> int:
    from .sources.guides import load_text

    async def loader():
        yield load_text(Path(args.file), args.url, args.title, args.author or "")
    return asyncio.run(_guides_ingest(loader, args))


def cmd_guides_list(args) -> int:
    from .sources.guides import GuideKB

    s = load_settings()
    kb = GuideKB(s.data_dir)
    if not kb.path.exists():
        _print("가이드 지식 베이스가 비어 있습니다.")
        return 0
    champs = load_cached(s.data_dir, s.locale)
    con = kb.connect(read_only=True)
    try:
        for title, author, url, n in con.execute("""
            SELECT s.title, s.author, s.url, count(c.claim_id) FROM guide_sources s
            LEFT JOIN guide_claims c USING (source_id) GROUP BY ALL ORDER BY 1""").fetchall():
            _print(f"- {title} ({author}) 주장 {n}개  {url}")
        if args.verbose:
            for cid, topic, text in con.execute("SELECT champion_id, topic, text FROM guide_claims").fetchall():
                _print(f"    [{champs.name(cid) if champs and cid else '공통'}/{topic}] {text}")
    finally:
        con.close()
    return 0


# ---- lcu -------------------------------------------------------------------

async def _lcu_status() -> int:
    from .lcu.client import LcuClient
    from .lcu.connection import find_credentials

    creds = find_credentials()
    if not creds:
        _print("롤 클라이언트를 찾지 못했습니다.")
        return 1
    client = LcuClient(creds)
    try:
        me = await client.current_summoner()
        phase = await client.gameflow_phase()
        name = f"{me.get('gameName', '?')}#{me.get('tagLine', '')}" if me else "?"
        _print(f"접속됨: {name}  현재 단계: {phase}")
    finally:
        await client.aclose()
    return 0


def cmd_lcu_status(_args) -> int:
    return asyncio.run(_lcu_status())


POS_KO = {"top": "탑", "jungle": "정글", "middle": "미드", "bottom": "원딜", "utility": "서폿", "": "?"}
STAGE_KO = {
    "planning": "선픽 의도 표시",
    "banning": "밴 진행",
    "pre_my_pick": "내 픽 전 → 픽/밴 추천 단계",
    "post_my_pick": "내 픽 확정 → 조합 브리핑 갱신",
    "final": "전원 확정 → 최종 게임 플랜",
}


def render_state(state: ChampSelectState, champs: ChampionIndex | None) -> str:
    name = champs.name if champs else (lambda cid: f"#{cid}" if cid else "-")

    def fmt(slot, mine=False):
        champ = name(slot.shown_champion)
        if not slot.locked and slot.shown_champion:
            champ += "(선택중)"
        mark = " ◀ 나" if mine else ""
        if not slot.position:  # 솔랭 적팀은 포지션이 공개되지 않음
            return f"{champ}{mark}"
        return f"{POS_KO.get(slot.position, slot.position)}:{champ}{mark}"

    lines = [
        f"── {STAGE_KO[state.stage.value]}  [timer={state.timer_phase}]",
        "  아군: " + ", ".join(fmt(s, s.cell_id == state.local_cell_id) for s in state.allies),
        "  적군: " + ", ".join(fmt(s) for s in state.enemies),
        "  밴  : 아군 " + " ".join(name(b) for b in state.ally_bans)
        + " / 적군 " + " ".join(name(b) for b in state.enemy_bans),
    ]
    if state.me and not state.is_jungle:
        lines.append(f"  (참고: 이번 판 내 포지션은 {POS_KO.get(state.my_position, state.my_position)})")
    return "\n".join(lines)


async def _lcu_watch(args) -> int:
    from .lcu.client import watch_champ_select
    from .lcu.replay import replay

    s = load_settings()
    champs = load_cached(s.data_dir, s.locale)
    if champs is None:
        _print("(챔피언 이름을 보려면 먼저 `loldosa ddragon sync`)")

    if args.replay:
        source = replay(Path(args.replay), interval=args.interval)
        _print(f"재생: {args.replay}")
    else:
        source = watch_champ_select(interval=args.interval)
        _print("챔피언 선택을 기다리는 중… (Ctrl+C 종료)")

    record = open(args.record, "a", encoding="utf-8") if args.record else None
    try:
        if record:
            # 녹화는 원본 세션을 그대로 저장해야 하므로 별도 루프
            return await _record_loop(record, args.interval, champs)
        async for state in source:
            _print(render_state(state, champs) if state else "── 챔피언 선택 종료")
    except KeyboardInterrupt:
        pass
    finally:
        if record:
            record.close()
    return 0


async def _record_loop(out, interval: float, champs) -> int:
    from .lcu.champselect import parse_session
    from .lcu.client import LcuClient
    from .lcu.connection import find_credentials

    _print(f"녹화 중 → {out.name} (Ctrl+C 종료)")
    client = None
    last_raw = None
    while True:
        if client is None:
            creds = find_credentials()
            if not creds:
                await asyncio.sleep(3)
                continue
            client = LcuClient(creds)
        session = await client.champ_select_session()
        raw = json.dumps(session, ensure_ascii=False, sort_keys=True)
        if raw != last_raw and (session is not None or last_raw is not None):
            out.write(raw + "\n")
            out.flush()
            if session:
                _print(render_state(parse_session(session), champs))
            last_raw = raw
        await asyncio.sleep(interval)


def cmd_lcu_watch(args) -> int:
    try:
        return asyncio.run(_lcu_watch(args))
    except KeyboardInterrupt:
        return 0


# ---- main ------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="loldosa", description="정글러 챔피언 선택 브리핑 도구")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="환경 점검").set_defaults(func=cmd_doctor)

    dd = sub.add_parser("ddragon", help="Data Dragon").add_subparsers(dest="sub", required=True)
    sync = dd.add_parser("sync", help="챔피언 데이터 받기")
    sync.add_argument("--version", help="패치 버전 (기본: 최신)")
    sync.set_defaults(func=cmd_ddragon_sync)

    riot = sub.add_parser("riot", help="Riot 웹 API").add_subparsers(dest="sub", required=True)
    riot.add_parser("check", help="API 키 동작 확인").set_defaults(func=cmd_riot_check)

    def collect_args(c):
        c.add_argument("--bucket", nargs="+", default=["apex", "emerald", "platinum"],
                       choices=["apex", "diamond", "emerald", "platinum"])
        c.add_argument("--players", type=int, default=50, help="경기 목록을 스캔할 플레이어 수")
        c.add_argument("--per-player", type=int, default=20)
        c.add_argument("--days", type=int, default=14)
        c.add_argument("--max-matches", type=int, default=300, help="버킷당 이번 실행 다운로드 상한")
        c.add_argument("--reseed", action="store_true", help="리그 목록을 다시 받아 플레이어 갱신")

    sub.add_parser("analyze", help="수집 데이터 → 통계 DB").set_defaults(func=cmd_analyze)
    sub.add_parser("reprocess", help="보관된 원본으로 경기 테이블 재생성 (업데이트 후 1회)").set_defaults(func=cmd_reprocess)
    up = sub.add_parser("update", help="챔피언 데이터 갱신 + 수집 + 분석 한 번에")
    collect_args(up)
    up.add_argument("--skip-pro", action="store_true", help="프로 대회 데이터 수집 건너뛰기")
    up.set_defaults(func=cmd_update)

    app = sub.add_parser("app", help="브리핑 앱 실행")
    app.add_argument("--replay", help="녹화 파일로 데모 실행")
    app.add_argument("--interval", type=float, default=2.0, help="재생 간격(초)")
    app.add_argument("--browser", action="store_true", help="창 대신 브라우저로 열기")
    app.add_argument("--port", type=int, default=8765)
    app.add_argument("--no-ai", action="store_true", help="Claude 코칭 끄기")
    app.set_defaults(func=cmd_app)

    rv = sub.add_parser("review", help="내 최근 경기 리뷰 (닉네임#태그)")
    rv.add_argument("riot_id", nargs="?", help="예: 'Hide on bush#KR1' (생략 시 저장된 값)")
    rv.add_argument("--count", type=int, default=10, help="가져올 경기 수")
    rv.add_argument("--show", type=int, default=3, help="콘솔에 출력할 경기 수")
    rv.set_defaults(func=cmd_review)

    ai = sub.add_parser("ai", help="AI 코치(Claude Code)").add_subparsers(dest="sub", required=True)
    ai.add_parser("check", help="Claude Code 구독 호출 확인").set_defaults(func=cmd_ai_check)

    pro = sub.add_parser("pro", help="프로 대회 데이터 (Leaguepedia)").add_subparsers(dest="sub", required=True)
    ps = pro.add_parser("sync", help="프로 정글 기록 수집")
    ps.add_argument("--days", type=int, default=90)
    ps.set_defaults(func=cmd_pro_sync)

    gd = sub.add_parser("guides", help="전문가 가이드 지식 베이스").add_subparsers(dest="sub", required=True)
    ga = gd.add_parser("add", help="유튜브 영상 자막에서 조언 추출")
    ga.add_argument("urls", nargs="+")
    ga.set_defaults(func=cmd_guides_add)
    gs = gd.add_parser("search", help="유튜브 검색 → 자막 → 추출 (예: '리신 정글 강의')")
    gs.add_argument("query", nargs="+")
    gs.add_argument("--max", type=int, default=3, help="검색어당 영상 수")
    gs.set_defaults(func=cmd_guides_search)
    gt = gd.add_parser("add-text", help="가이드 글(텍스트 파일)에서 조언 추출")
    gt.add_argument("file")
    gt.add_argument("--url", required=True, help="원문 주소 (출처 표시용)")
    gt.add_argument("--title", required=True)
    gt.add_argument("--author")
    gt.set_defaults(func=cmd_guides_text)
    gl = gd.add_parser("list", help="저장된 가이드 보기")
    gl.set_defaults(func=cmd_guides_list)

    col = sub.add_parser("collect", help="경기·타임라인 수집 (재개 가능)")
    collect_args(col)
    col.set_defaults(func=cmd_collect)

    lcu = sub.add_parser("lcu", help="롤 클라이언트(로컬)").add_subparsers(dest="sub", required=True)
    lcu.add_parser("status", help="접속 확인").set_defaults(func=cmd_lcu_status)
    watch = lcu.add_parser("watch", help="챔피언 선택 감시")
    watch.add_argument("--replay", help="녹화 파일(JSONL) 재생")
    watch.add_argument("--record", help="실제 챔선을 JSONL 로 녹화")
    watch.add_argument("--interval", type=float, default=1.0)
    watch.set_defaults(func=cmd_lcu_watch)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
