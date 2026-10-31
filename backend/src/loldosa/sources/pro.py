"""프로 대회 정글 데이터 (Leaguepedia Cargo API, 공개).

정글러의 챔피언·승패와 경기별 오브젝트(유충/드래곤/전령/바론/아타칸) 수를 받아
data/pro.duckdb 에 저장한다. 분 단위 위치 데이터는 공개돼 있지 않아서 동선 분석에는 쓰지 않는다.

익명 요청은 레이트 리밋이 엄격해서 요청 사이에 쉬고, 리밋이 걸리면 지수 백오프로 재시도한다.
"""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import date, timedelta
from pathlib import Path

import duckdb
import httpx

log = logging.getLogger(__name__)

API = "https://lol.fandom.com/api.php"
WIKI = "https://lol.fandom.com/wiki/"
PAGE = 500

FIELDS = [
    "SP.GameId=game_id", "SP.Champion=champion", "SP.PlayerWin=win", "SP.Team=team", "SP.Link=player",
    "SG.Tournament=tournament", "SG.OverviewPage=overview", "SG.Patch=patch", "SG.DateTime_UTC=played_at",
    "SG.Gamelength_Number=minutes", "SG.Team1=team1", "SG.Team2=team2",
    "SG.Team1Dragons=t1_dragons", "SG.Team2Dragons=t2_dragons",
    "SG.Team1VoidGrubs=t1_grubs", "SG.Team2VoidGrubs=t2_grubs",
    "SG.Team1RiftHeralds=t1_heralds", "SG.Team2RiftHeralds=t2_heralds",
    "SG.Team1Barons=t1_barons", "SG.Team2Barons=t2_barons",
    "SG.Team1Atakhans=t1_atakhans", "SG.Team2Atakhans=t2_atakhans",
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS pro_jungle (
    game_id VARCHAR, team VARCHAR, player VARCHAR, champion VARCHAR, champion_id INTEGER,
    win BOOLEAN, tournament VARCHAR, overview VARCHAR, patch VARCHAR, played_at TIMESTAMP, minutes DOUBLE,
    own_dragons INTEGER, enemy_dragons INTEGER, own_grubs INTEGER, enemy_grubs INTEGER,
    own_heralds INTEGER, own_barons INTEGER, own_atakhans INTEGER,
    PRIMARY KEY (game_id, team)
);
"""


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


async def english_names(version: str) -> dict[str, int]:
    """Leaguepedia 는 영어 챔피언 이름을 쓴다 → 영어 이름/키 → championId."""
    async with httpx.AsyncClient(timeout=20) as http:
        r = await http.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json")
        r.raise_for_status()
    out = {}
    for c in r.json()["data"].values():
        out[norm(c["name"])] = int(c["key"])
        out[norm(c["id"])] = int(c["key"])
    out[norm("Nunu")] = out.get(norm("Nunu & Willump"), out.get("nunu", 0))
    return out


def _int(v) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


async def cargo(http: httpx.AsyncClient, params: dict, retries: int = 6) -> list[dict]:
    base = {"action": "cargoquery", "format": "json", "limit": PAGE}
    for attempt in range(retries):
        r = await http.get(API, params=base | params)
        data = r.json() if r.status_code == 200 else {}
        if "cargoquery" in data:
            return [row["title"] for row in data["cargoquery"]]
        code = (data.get("error") or {}).get("code", r.status_code)
        wait = min(10 * 2**attempt, 120)
        log.warning("Leaguepedia %s, %ss 후 재시도", code, wait)
        await asyncio.sleep(wait)
    raise RuntimeError("Leaguepedia 요청 실패 (레이트 리밋). 잠시 후 다시 실행하세요.")


async def fetch_pro_jungle(since: date, say=print) -> list[dict]:
    rows: list[dict] = []
    async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "LoLDosa personal jungle study tool"}) as http:
        offset = 0
        while True:
            page = await cargo(http, {
                "tables": "ScoreboardPlayers=SP,ScoreboardGames=SG",
                "join_on": "SP.GameId=SG.GameId",
                "fields": ",".join(FIELDS),
                "where": f"SP.Role='Jungle' AND SG.DateTime_UTC >= '{since.isoformat()}'",
                "order_by": "SG.DateTime_UTC DESC",
                "offset": offset,
            })
            rows += page
            say(f"  프로 정글 기록 {len(rows)}건")
            if len(page) < PAGE:
                break
            offset += PAGE
            await asyncio.sleep(3)
    return rows


def to_records(rows: list[dict], names: dict[str, int]) -> list[tuple]:
    out = []
    for r in rows:
        side1 = r["team"] == r["team1"]
        o, e = ("t1", "t2") if side1 else ("t2", "t1")
        out.append((
            r["game_id"], r["team"], r["player"], r["champion"], names.get(norm(r["champion"] or ""), 0),
            r["win"] == "Yes", r["tournament"], r["overview"], r["patch"], r["played_at"],
            float(r["minutes"] or 0),
            _int(r[f"{o}_dragons"]), _int(r[f"{e}_dragons"]), _int(r[f"{o}_grubs"]), _int(r[f"{e}_grubs"]),
            _int(r[f"{o}_heralds"]), _int(r[f"{o}_barons"]), _int(r[f"{o}_atakhans"]),
        ))
    return out


async def sync_pro(data_dir: Path, ddragon_version: str, days: int = 90, say=print) -> int:
    since = date.today() - timedelta(days=days)
    say(f"Leaguepedia 프로 대회 정글 기록 수집 ({since} 이후)…")
    rows = await fetch_pro_jungle(since, say)
    names = await english_names(ddragon_version)
    recs = to_records(rows, names)
    con = duckdb.connect(str(data_dir / "pro.duckdb"))
    try:
        con.execute(SCHEMA).fetchall()
        con.executemany(
            f"INSERT OR REPLACE INTO pro_jungle VALUES ({','.join('?' * 18)})", recs)
        unmapped = sorted({r[3] for r in recs if not r[4]})
        if unmapped:
            say(f"  챔피언 이름 매칭 실패: {unmapped}")
        n = con.execute("SELECT count(*) FROM pro_jungle").fetchall()[0][0]
    finally:
        con.close()
    return n
