"""수집 DB (data/matches.duckdb). 수집기만 쓰기, 분석기는 읽기.

원본 JSON 은 data/raw/<match_id>.json.gz 로 따로 보관해 재분석할 수 있게 한다.
"""

from __future__ import annotations

import gzip
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pyarrow as pa

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    puuid VARCHAR PRIMARY KEY,
    bucket VARCHAR,          -- apex | platinum
    tier VARCHAR, division VARCHAR, lp INTEGER,
    seeded_at TIMESTAMP, scanned_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS match_queue (
    match_id VARCHAR PRIMARY KEY,
    bucket VARCHAR,
    status VARCHAR DEFAULT 'pending',   -- pending | done | skipped | error
    discovered_at TIMESTAMP,
    error VARCHAR
);
CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR PRIMARY KEY,
    bucket VARCHAR,
    patch VARCHAR,           -- "16.21"
    game_version VARCHAR,
    game_start TIMESTAMP,
    duration_s INTEGER,
    queue_id INTEGER,
    winner_team INTEGER
);
CREATE TABLE IF NOT EXISTS participants (
    match_id VARCHAR, participant_id INTEGER, puuid VARCHAR,
    team_id INTEGER, position VARCHAR, champion_id INTEGER, win BOOLEAN,
    kills INTEGER, deaths INTEGER, assists INTEGER,
    spell1 INTEGER, spell2 INTEGER, champ_level INTEGER,
    gold INTEGER, damage_to_champs INTEGER,
    vision_score INTEGER, wards_placed INTEGER, control_wards INTEGER,
    neutral_minions INTEGER, enemy_jungle_minions INTEGER,
    PRIMARY KEY (match_id, participant_id)
);
CREATE TABLE IF NOT EXISTS bans (
    match_id VARCHAR, team_id INTEGER, pick_turn INTEGER, champion_id INTEGER
);
CREATE TABLE IF NOT EXISTS frames (
    match_id VARCHAR, minute INTEGER, participant_id INTEGER,
    x INTEGER, y INTEGER, level INTEGER, xp INTEGER, total_gold INTEGER,
    jungle_cs INTEGER, lane_cs INTEGER,
    PRIMARY KEY (match_id, minute, participant_id)
);
CREATE TABLE IF NOT EXISTS events (
    match_id VARCHAR, ts_ms INTEGER, type VARCHAR,
    participant_id INTEGER,      -- killer / creator / buyer
    victim_id INTEGER,
    assists INTEGER[],
    team_id INTEGER,             -- killer team (elite/building) or owner team
    monster_type VARCHAR, monster_sub_type VARCHAR,
    building_type VARCHAR, lane VARCHAR, ward_type VARCHAR,
    x INTEGER, y INTEGER
);
"""

COLUMNS = {
    "matches": ["match_id", "bucket", "patch", "game_version", "game_start", "duration_s", "queue_id", "winner_team"],
    "participants": ["match_id", "participant_id", "puuid", "team_id", "position", "champion_id", "win",
                     "kills", "deaths", "assists", "spell1", "spell2", "champ_level", "gold",
                     "damage_to_champs", "vision_score", "wards_placed", "control_wards",
                     "neutral_minions", "enemy_jungle_minions"],
    "bans": ["match_id", "team_id", "pick_turn", "champion_id"],
    "frames": ["match_id", "minute", "participant_id", "x", "y", "level", "xp", "total_gold",
               "jungle_cs", "lane_cs"],
    "events": ["match_id", "ts_ms", "type", "participant_id", "victim_id", "assists", "team_id",
               "monster_type", "monster_sub_type", "building_type", "lane", "ward_type", "x", "y"],
}

KEEP_EVENTS = {
    "CHAMPION_KILL", "ELITE_MONSTER_KILL", "BUILDING_KILL", "TURRET_PLATE_DESTROYED",
    "WARD_PLACED", "WARD_KILL", "CHAMPION_SPECIAL_KILL", "DRAGON_SOUL_GIVEN",
}


def now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def patch_of(game_version: str) -> str:
    return ".".join(game_version.split(".")[:2])


def _bulk_insert(con: duckdb.DuckDBPyConnection, table: str, rows: list[tuple]) -> None:
    if not rows:
        return
    cols = COLUMNS[table]
    tbl = pa.Table.from_pydict({c: [r[i] for r in rows] for i, c in enumerate(cols)})
    con.register("_bulk", tbl)
    try:
        con.execute(f"INSERT INTO {table} ({', '.join(cols)}) SELECT {', '.join(cols)} FROM _bulk").fetchall()
    finally:
        con.unregister("_bulk")


class MatchStore:
    def __init__(self, data_dir: Path, read_only: bool = False) -> None:
        self.data_dir = data_dir
        self.raw_dir = data_dir / "raw"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / "matches.duckdb"
        self.con = duckdb.connect(str(self.path), read_only=read_only)
        if not read_only:
            self._x(SCHEMA)

    def _x(self, sql: str, params: list | None = None) -> list[tuple]:
        """실행하고 결과를 끝까지 읽는다 (DuckDB 2.x 는 미완료 결과가 있으면 다음 작업을 막음)."""
        return self.con.execute(sql, params or []).fetchall()

    def close(self) -> None:
        self.con.close()

    # ---- players / queue -------------------------------------------------

    def upsert_players(self, rows: list[dict], bucket: str) -> int:
        ts = now()
        seen: dict[str, tuple] = {}
        for r in rows:
            if r.get("puuid"):
                seen[r["puuid"]] = (r["puuid"], bucket, r.get("tier"), r.get("rank"), r.get("leaguePoints"), ts)
        if not seen:
            return 0
        data = list(seen.values())
        cols = ["puuid", "bucket", "tier", "division", "lp", "seeded_at"]
        self.con.register("_p", pa.Table.from_pydict({c: [r[i] for r in data] for i, c in enumerate(cols)}))
        try:
            self._x(
                """INSERT INTO players (puuid, bucket, tier, division, lp, seeded_at)
                   SELECT puuid, bucket, tier, division, lp, seeded_at FROM _p
                   ON CONFLICT (puuid) DO UPDATE SET bucket=excluded.bucket, tier=excluded.tier,
                   division=excluded.division, lp=excluded.lp, seeded_at=excluded.seeded_at""")
        finally:
            self.con.unregister("_p")
        return len(data)

    def player_count(self, bucket: str) -> int:
        return self._x("SELECT count(*) FROM players WHERE bucket = ?", [bucket])[0][0]

    def players_to_scan(self, bucket: str, limit: int, rescan_hours: float = 12) -> list[str]:
        rows = self._x(
            """SELECT puuid FROM players WHERE bucket = ?
               AND (scanned_at IS NULL OR scanned_at < now()::TIMESTAMP - to_hours(CAST(? AS BIGINT)))
               ORDER BY scanned_at NULLS FIRST, lp DESC LIMIT ?""",
            [bucket, int(rescan_hours), limit],
        )
        return [r[0] for r in rows]

    def mark_scanned(self, puuid: str) -> None:
        self._x("UPDATE players SET scanned_at = ? WHERE puuid = ?", [now(), puuid])

    def enqueue(self, match_ids: list[str], bucket: str) -> int:
        if not match_ids:
            return 0
        before = self._x("SELECT count(*) FROM match_queue")[0][0]
        ts = now()
        tbl = pa.Table.from_pydict({"match_id": match_ids, "bucket": [bucket] * len(match_ids),
                                    "discovered_at": [ts] * len(match_ids)})
        self.con.register("_q", tbl)
        try:
            self._x("""INSERT INTO match_queue (match_id, bucket, discovered_at)
                                SELECT match_id, bucket, discovered_at FROM _q ON CONFLICT DO NOTHING""")
        finally:
            self.con.unregister("_q")
        return self._x("SELECT count(*) FROM match_queue")[0][0] - before

    def pending(self, limit: int, bucket: str | None = None) -> list[tuple[str, str]]:
        q = "SELECT match_id, bucket FROM match_queue WHERE status='pending'"
        params: list = []
        if bucket:
            q += " AND bucket = ?"
            params.append(bucket)
        q += " ORDER BY discovered_at LIMIT ?"
        return self._x(q, params + [limit])

    def requeue_errors(self) -> int:
        n = self._x("SELECT count(*) FROM match_queue WHERE status='error'")[0][0]
        self._x("UPDATE match_queue SET status='pending', error=NULL WHERE status='error'")
        return n

    def set_status(self, match_id: str, status: str, error: str | None = None) -> None:
        self._x("UPDATE match_queue SET status=?, error=? WHERE match_id=?", [status, error, match_id])

    # ---- ingest ----------------------------------------------------------

    def save_raw(self, match_id: str, match: dict, timeline: dict) -> None:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        with gzip.open(self.raw_dir / f"{match_id}.json.gz", "wt", encoding="utf-8") as f:
            json.dump({"match": match, "timeline": timeline}, f, separators=(",", ":"))

    def load_raw(self, match_id: str) -> tuple[dict, dict] | None:
        path = self.raw_dir / f"{match_id}.json.gz"
        if not path.exists():
            return None
        with gzip.open(path, "rt", encoding="utf-8") as f:
            d = json.load(f)
        return d["match"], d["timeline"]

    def ingest(self, match: dict, timeline: dict, bucket: str) -> None:
        rows = normalize(match, timeline, bucket)
        mid = rows["matches"][0][0]
        self._x("BEGIN")
        try:
            for table in COLUMNS:
                self._x(f"DELETE FROM {table} WHERE match_id = ?", [mid])
                _bulk_insert(self.con, table, rows[table])
            self._x("COMMIT")
        except Exception:
            self._x("ROLLBACK")
            raise

    def counts(self) -> dict[str, int]:
        out = {t: self._x(f"SELECT count(*) FROM {t}")[0][0]
               for t in ("players", "matches")}
        for status, n in self._x("SELECT status, count(*) FROM match_queue GROUP BY 1"):
            out[f"queue_{status}"] = n
        return out


def normalize(match: dict, timeline: dict, bucket: str) -> dict[str, list]:
    info = match["info"]
    mid = match["metadata"]["matchId"]
    winner = next((t["teamId"] for t in info["teams"] if t.get("win")), 0)
    start = datetime.fromtimestamp(info["gameStartTimestamp"] / 1000, tz=timezone.utc).replace(tzinfo=None)
    out: dict[str, list] = {
        "matches": [(mid, bucket, patch_of(info["gameVersion"]), info["gameVersion"], start,
                   info["gameDuration"], info["queueId"], winner)],
        "participants": [],
        "bans": [],
        "frames": [],
        "events": [],
    }
    for p in info["participants"]:
        ch = p.get("challenges") or {}
        out["participants"].append((
            mid, p["participantId"], p["puuid"], p["teamId"], p.get("teamPosition") or "",
            p["championId"], p["win"], p["kills"], p["deaths"], p["assists"],
            p["summoner1Id"], p["summoner2Id"], p["champLevel"], p["goldEarned"],
            p["totalDamageDealtToChampions"], p.get("visionScore", 0), p.get("wardsPlaced", 0),
            p.get("visionWardsBoughtInGame", 0), p.get("neutralMinionsKilled", 0),
            int(ch.get("enemyJungleMonsterKills", 0) or 0),
        ))
    for t in info["teams"]:
        for b in t.get("bans") or []:
            if b.get("championId", -1) > 0:
                out["bans"].append((mid, t["teamId"], b["pickTurn"], b["championId"]))

    for minute, frame in enumerate(timeline["info"]["frames"]):
        for pid, pf in frame["participantFrames"].items():
            pos = pf.get("position") or {}
            out["frames"].append((
                mid, minute, int(pid), pos.get("x"), pos.get("y"), pf.get("level"), pf.get("xp"),
                pf.get("totalGold"), pf.get("jungleMinionsKilled"), pf.get("minionsKilled"),
            ))
        for e in frame["events"]:
            if e["type"] not in KEEP_EVENTS:
                continue
            pos = e.get("position") or {}
            out["events"].append((
                mid, e["timestamp"], e["type"],
                e.get("killerId", e.get("creatorId")),
                e.get("victimId"),
                e.get("assistingParticipantIds") or [],
                e.get("killerTeamId", e.get("teamId")),
                e.get("monsterType"), e.get("monsterSubType"),
                e.get("buildingType"), e.get("laneType"), e.get("wardType"),
                pos.get("x"), pos.get("y"),
            ))
    return out
