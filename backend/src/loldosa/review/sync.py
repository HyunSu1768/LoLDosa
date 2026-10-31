"""내 경기 가져오기: Riot ID → PUUID → 최근 솔랭 → match + timeline (data/personal.duckdb).

고티어 통계(matches.duckdb)와 섞이지 않도록 따로 저장한다.
"""

from __future__ import annotations

from ..riot.client import RiotClient
from ..store.matches import MatchStore

PERSONAL_DB = "personal.duckdb"
# 복기 대상: 소환사의 협곡 5:5 (일반 400·비공개 선택 430·솔랭 420·자랭 440·빠른 대전 490). 칼바람 등은 뺀다.
SR_QUEUES = {400, 420, 430, 440, 490}


def split_riot_id(riot_id: str) -> tuple[str, str]:
    name, sep, tag = riot_id.strip().rpartition("#")
    if not sep or not name or not tag:
        raise ValueError("Riot ID 는 '닉네임#태그' 형식이어야 합니다 (예: Hide on bush#KR1)")
    return name.strip(), tag.strip()


async def resolve_puuid(riot: RiotClient, riot_id: str) -> str:
    name, tag = split_riot_id(riot_id)
    acc = await riot.account_by_riot_id(name, tag)
    if not acc or not acc.get("puuid"):
        raise ValueError(f"'{riot_id}' 계정을 찾지 못했어요. 닉네임과 태그를 확인해 주세요.")
    return acc["puuid"]


async def sync_personal(riot: RiotClient, store: MatchStore, puuid: str, count: int = 10,
                        queue: int | None = None, say=print) -> list[str]:
    """queue 를 안 주면 협곡 게임 전부 (솔랭만 하던 예전 방식은 일반·자랭을 놓쳤다)."""
    ids = await riot.match_ids(puuid, queue=queue, count=count)
    new = [m for m in ids if not store.has_match(m)]
    for i, mid in enumerate(new, 1):
        match = await riot.match(mid)
        if not match or (queue is None and match["info"].get("queueId") not in SR_QUEUES):
            continue  # 칼바람 등: 타임라인까지 받지 않는다
        timeline = await riot.timeline(mid)
        if timeline:
            store.save_raw(mid, match, timeline)
            store.ingest(match, timeline, "personal")
        say(f"  {i}/{len(new)} {mid}")
    return ids


def list_matches(store: MatchStore, puuid: str, limit: int = 20) -> list[dict]:
    rows = store._x("""
        SELECT m.match_id, m.game_start, m.duration_s, m.patch, p.champion_id, p.position, p.win,
               p.kills, p.deaths, p.assists,
               (SELECT e.champion_id FROM participants e WHERE e.match_id = m.match_id
                  AND e.position = 'JUNGLE' AND e.team_id <> p.team_id) AS enemy_jungler
        FROM matches m JOIN participants p ON p.match_id = m.match_id AND p.puuid = ?
        ORDER BY m.game_start DESC LIMIT ?""", [puuid, limit])
    cols = ["match_id", "game_start", "duration_s", "patch", "champion_id", "position", "win",
            "kills", "deaths", "assists", "enemy_jungler"]
    return [dict(zip(cols, r)) for r in rows]
