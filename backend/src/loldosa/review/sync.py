"""내 경기 가져오기: Riot ID → PUUID → 최근 솔랭 → match + timeline (data/personal.duckdb).

고티어 통계(matches.duckdb)와 섞이지 않도록 따로 저장한다.
"""

from __future__ import annotations

from ..riot.client import RiotClient
from ..store.matches import MatchStore

PERSONAL_DB = "personal.duckdb"


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
                        queue: int = 420, say=print) -> list[str]:
    ids = await riot.match_ids(puuid, queue=queue, count=count)
    new = [m for m in ids if not store.has_match(m)]
    for i, mid in enumerate(new, 1):
        match, timeline = await riot.match(mid), await riot.timeline(mid)
        if match and timeline:
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
