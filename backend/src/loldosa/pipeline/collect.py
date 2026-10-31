"""수집 파이프라인: 플레이어 시드 → 경기 ID 큐 → match + timeline 저장.

버킷
- apex:     KR 챌린저/그랜드마스터/마스터
- platinum: KR 플래티넘 I~IV (본인 티어대)

모든 단계는 재개 가능하다. 중단 후 다시 실행하면 남은 것부터 이어서 한다.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass

from ..riot.client import RiotClient
from ..store.matches import MatchStore

log = logging.getLogger(__name__)

SOLO_QUEUE_ID = 420
DIVISIONS = ("I", "II", "III", "IV")


@dataclass
class CollectConfig:
    bucket: str = "apex"
    players: int = 50            # 이번 실행에서 경기 목록을 스캔할 플레이어 수
    matches_per_player: int = 20
    days: int = 14
    max_matches: int = 300       # 이번 실행에서 받을 경기 수 상한
    plat_pages: int = 2          # 플래티넘 디비전당 리그 페이지 수 (페이지당 ~205명)
    concurrency: int = 4
    reseed: bool = False


async def seed_players(riot: RiotClient, store: MatchStore, cfg: CollectConfig) -> int:
    total = 0
    if cfg.bucket == "apex":
        for tier in ("challenger", "grandmaster", "master"):
            league = await riot.apex_league(tier)
            entries = [dict(e, tier=league.get("tier", tier.upper())) for e in (league or {}).get("entries", [])]
            total += store.upsert_players(entries, "apex")
    elif cfg.bucket == "platinum":
        for div in DIVISIONS:
            for page in range(1, cfg.plat_pages + 1):
                entries = await riot.league_entries("PLATINUM", div, page)
                if not entries:
                    break
                total += store.upsert_players(entries, "platinum")
    else:
        raise ValueError(f"unknown bucket {cfg.bucket}")
    return total


async def discover_matches(riot: RiotClient, store: MatchStore, cfg: CollectConfig) -> int:
    since = int(time.time()) - cfg.days * 86400
    added = 0
    for puuid in store.players_to_scan(cfg.bucket, cfg.players):
        ids = await riot.match_ids(puuid, queue=SOLO_QUEUE_ID, count=cfg.matches_per_player, start_time=since)
        added += store.enqueue(ids, cfg.bucket)
        store.mark_scanned(puuid)
    return added


async def fetch_matches(riot: RiotClient, store: MatchStore, cfg: CollectConfig, progress=None) -> int:
    store.requeue_errors()
    todo = store.pending(cfg.max_matches, cfg.bucket)
    sem = asyncio.Semaphore(cfg.concurrency)
    done = 0

    async def one(match_id: str, bucket: str) -> None:
        nonlocal done
        async with sem:
            try:
                match, timeline = await asyncio.gather(riot.match(match_id), riot.timeline(match_id))
                if not match or not timeline:
                    store.set_status(match_id, "skipped", "not found")
                    return
                if match["info"].get("queueId") != SOLO_QUEUE_ID or match["info"]["gameDuration"] < 600:
                    store.set_status(match_id, "skipped", "remake/other queue")
                    return
                store.save_raw(match_id, match, timeline)
                store.ingest(match, timeline, bucket)
                store.set_status(match_id, "done")
                done += 1
                if progress:
                    progress(done, len(todo))
            except Exception as e:  # 한 경기 실패가 전체를 멈추지 않게
                log.warning("match %s failed: %s", match_id, e)
                store.set_status(match_id, "error", str(e)[:300])

    await asyncio.gather(*(one(m, b) for m, b in todo))
    return done


async def run_collect(riot: RiotClient, store: MatchStore, cfg: CollectConfig, say=print) -> dict:
    if store.player_count(cfg.bucket) == 0 or cfg.reseed:
        say(f"[{cfg.bucket}] 플레이어 시드 수집…")
        say(f"  {await seed_players(riot, store, cfg)}명")
    say(f"[{cfg.bucket}] 경기 목록 스캔 (플레이어 {cfg.players}명, 최근 {cfg.days}일)…")
    say(f"  새 경기 {await discover_matches(riot, store, cfg)}개 큐에 추가")
    say(f"[{cfg.bucket}] 경기·타임라인 다운로드 (최대 {cfg.max_matches}개)…")

    def progress(n, total):
        if n % 10 == 0 or n == total:
            say(f"  {n}/{total}")

    n = await fetch_matches(riot, store, cfg, progress)
    say(f"  완료 {n}개")
    return store.counts()
