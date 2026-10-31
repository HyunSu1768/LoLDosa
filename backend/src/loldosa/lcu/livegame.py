"""내 게임 정밀 기록: 게임 중 Live Client Data API(https://127.0.0.1:2999, Riot 공식)를 2초마다 기록한다.

Match-V5 타임라인은 1분 단위라 '언제 귀환했나, 골드를 얼마나 오래 들고 있었나, CS 가 멈춘 구간' 같은 건
정확히 잴 수 없다. 내 PC 에서 도는 게임만큼은 이 API 로 초 단위 기록을 남길 수 있다.
게임 중에는 아무것도 보여주지 않는다 (기록만). 분석은 게임이 끝난 뒤 복기에서 한다.
"""

from __future__ import annotations

import asyncio
import gzip
import json
import logging
from pathlib import Path

import httpx

log = logging.getLogger(__name__)
LIVE_URL = "https://127.0.0.1:2999/liveclientdata/allgamedata"


def _me(data: dict) -> dict | None:
    ap = data.get("activePlayer") or {}
    name = ap.get("riotId") or ap.get("summonerName")
    return next((p for p in data.get("allPlayers", []) if (p.get("riotId") or p.get("summonerName")) == name), None)


def compact(data: dict) -> dict | None:
    """한 번 받은 응답에서 필요한 것만 (용량을 줄인다)."""
    me = _me(data)
    ap = data.get("activePlayer") or {}
    if not me:
        return None
    sc = me.get("scores") or {}
    return {"t": round((data.get("gameData") or {}).get("gameTime", 0), 1), "lvl": ap.get("level", me.get("level")),
            "gold": round(ap.get("currentGold", 0)), "cs": sc.get("creepScore", 0), "k": sc.get("kills", 0),
            "d": sc.get("deaths", 0), "a": sc.get("assists", 0), "dead": bool(me.get("isDead")),
            "items": sorted(i.get("itemID", 0) for i in me.get("items", []))}


async def record(out_dir: Path, game_id: int, interval: float = 2.0, url: str = LIVE_URL,
                 give_up_s: float = 180.0) -> Path | None:
    """게임이 끝날 때까지 기록. 처음 연결까지 give_up_s 동안 기다리고, 연결이 끊기면 끝낸다."""
    rows, events, waited = [], [], 0.0
    async with httpx.AsyncClient(verify=False, timeout=3.0) as http:
        while True:
            try:
                r = await http.get(url)
                r.raise_for_status()
                data = r.json()
            except (httpx.HTTPError, ValueError):
                if rows:
                    break  # 게임 끝
                waited += interval
                if waited > give_up_s:
                    return None
                await asyncio.sleep(interval)
                continue
            if (c := compact(data)) and (not rows or c != {**rows[-1], "t": c["t"]}):
                rows.append(c)
            events = (data.get("events") or {}).get("Events", events)
            await asyncio.sleep(interval)
    if not rows:
        return None
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{game_id}.json.gz"
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump({"game_id": game_id, "rows": rows, "events": events}, f, ensure_ascii=False)
    return path


def load(out_dir: Path, game_id: int) -> dict | None:
    path = out_dir / f"{game_id}.json.gz"
    if not path.exists():
        return None
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def _mmss(t: float) -> str:
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


def summarize(rec: dict, until_s: float = 900.0) -> dict:
    """초 단위 기록 → 복기용 사실들 (15분까지)."""
    rows = [r for r in rec["rows"] if r["t"] <= until_s]
    out: dict = {"levels": {}, "shops": [], "rich_s": 0.0, "idle": [], "samples": len(rows)}
    if len(rows) < 2:
        return out
    for a, b in zip(rows, rows[1:]):
        dt = b["t"] - a["t"]
        # 레벨 2·3·4·6 찍은 시각
        for lv in (2, 3, 4, 6):
            if a["lvl"] < lv <= b["lvl"] and lv not in out["levels"]:
                out["levels"][lv] = b["t"]
        # 상점: 아이템이 바뀌고 골드가 줄면 (살아 있을 때 = 귀환, 죽어 있을 때 = 부활 대기 중 구매)
        if a["items"] != b["items"] and b["gold"] < a["gold"] - 100 and a["t"] > 60:
            out["shops"].append({"t": b["t"], "spent": a["gold"] - b["gold"], "dead": a["dead"] or b["dead"]})
        # 1,200골드 넘게 들고 살아 있던 시간 (귀환 미루기)
        if a["gold"] >= 1200 and not a["dead"]:
            out["rich_s"] += dt
    # CS 가 60초 넘게 안 오른 구간 (살아 있고 1:30 이후) = 정글링도 갱도 안 한 시간 후보
    start = None
    for a, b in zip(rows, rows[1:]):
        moving = b["cs"] > a["cs"] or b["k"] + b["a"] > a["k"] + a["a"] or a["dead"]
        if a["t"] < 90 or moving:
            if start is not None and a["t"] - start >= 60:
                out["idle"].append({"from": start, "to": a["t"]})
            start = None
        elif start is None:
            start = a["t"]
    out["rich_s"] = round(out["rich_s"])
    out["text"] = {
        "levels": " · ".join(f"{lv}레벨 {_mmss(t)}" for lv, t in sorted(out["levels"].items())),
        "shops": " · ".join(f"{_mmss(s['t'])}{'(죽어서)' if s['dead'] else ''} {s['spent']:,}골드" for s in out["shops"][:6]),
        "rich": f"15분까지 1,200골드 넘게 들고 버틴 시간 {out['rich_s'] // 60}분 {out['rich_s'] % 60}초",
        "idle": " · ".join(f"{_mmss(x['from'])}~{_mmss(x['to'])}" for x in out["idle"][:5]),
    }
    return out
