"""이미지 트레이닝용 '대표 동선': 평균 위치가 아니라 실제 한 판의 동선(메도이드)을 고른다.

평균을 내면 아무도 가지 않는 경로가 나오기 때문에, 같은 챔피언·진영·클리어 방식의 동선들 중
다른 동선들과의 거리 합이 가장 작은 실제 경기 하나를 대표로 쓴다.
"""

from __future__ import annotations

import json
import math

from .geometry import relative_region

PATH_MINUTES = range(1, 7)  # 1:00 ~ 6:00


def trajectories(con, prefix: str = "src.") -> dict[tuple[int, int, str], list[dict]]:
    """(챔피언, 진영, 클리어 방식) -> [{match_id, points:[{m,x,y,camps,region}]}]"""
    rows = con.execute(f"""
        SELECT p.match_id, p.participant_id, p.team_id, p.champion_id, f.minute, f.x, f.y, f.jungle_cs
        FROM {prefix}participants p JOIN {prefix}frames f ON f.match_id = p.match_id AND f.participant_id = p.participant_id
        WHERE p.position = 'JUNGLE' AND f.minute BETWEEN 1 AND 6
        ORDER BY p.match_id, p.participant_id, f.minute""").fetchall()
    by: dict[tuple, dict] = {}
    for mid, pid, team, champ, m, x, y, jcs in rows:
        if x is None:
            continue
        t = by.setdefault((mid, pid), {"match_id": mid, "team": team, "champ": champ, "points": []})
        t["points"].append({"m": m, "x": x, "y": y, "camps": (jcs or 0) // 4,
                            "region": relative_region(team, x, y)})
    out: dict[tuple, list] = {}
    for t in by.values():
        if len(t["points"]) != len(PATH_MINUTES):
            continue
        c3 = next(p["camps"] for p in t["points"] if p["m"] == 3)
        style = "full_clear" if c3 >= 6 else "partial" if c3 >= 4 else "three_or_less"
        for key in ((t["champ"], t["team"], style), (t["champ"], t["team"], "any")):
            out.setdefault(key, []).append(t)
    return out


def medoid(trajs: list[dict]) -> dict:
    def d(a, b):
        return sum(math.dist((p["x"], p["y"]), (q["x"], q["y"])) for p, q in zip(a["points"], b["points"]))

    if len(trajs) <= 2:
        return trajs[0]
    best, best_s = None, float("inf")
    for a in trajs:
        s = sum(d(a, b) for b in trajs)
        if s < best_s:
            best, best_s = a, s
    return best


def exact_events(con, prefix: str, match_id: str, pid: int) -> list[dict]:
    """대표 경기의 첫 6분 '정확한 시각' 이벤트: 귀환(구매), 킬·데스·어시스트, 오브젝트."""
    from .turns import shop_visits

    pur = con.execute(f"SELECT participant_id, ts_ms FROM {prefix}events WHERE match_id=? AND type='ITEM_PURCHASED'",
                      [match_id]).fetchall()
    kills = con.execute(f"""SELECT ts_ms, participant_id, victim_id, assists, x, y FROM {prefix}events
                            WHERE match_id=? AND type='CHAMPION_KILL' AND ts_ms <= 360000""", [match_id]).fetchall()
    team = con.execute(f"SELECT team_id FROM {prefix}participants WHERE match_id=? AND participant_id=?",
                       [match_id, pid]).fetchall()[0][0]
    out = []
    for v in shop_visits(pur, [(k[2], k[0]) for k in kills]):
        if v.participant_id == pid and v.ts_ms <= 360000:
            out.append({"t": v.ts_ms / 1000, "kind": "death_back" if v.death_back else "recall"})
    for ts, killer, victim, assists, x, y in kills:
        if victim == pid:
            out.append({"t": ts / 1000, "kind": "death", "where": relative_region(team, x, y)})
        elif killer == pid or pid in (assists or []):
            out.append({"t": ts / 1000, "kind": "kill" if killer == pid else "assist", "where": relative_region(team, x, y)})
    for ts, mt, tm in con.execute(f"""SELECT ts_ms, monster_type, team_id FROM {prefix}events
                                      WHERE match_id=? AND type='ELITE_MONSTER_KILL' AND ts_ms <= 360000""", [match_id]).fetchall():
        out.append({"t": ts / 1000, "kind": "objective", "monster": mt, "ours": tm == team})
    return sorted(out, key=lambda e: e["t"])


def build_medoids(con, prefix: str = "src.") -> list[tuple]:
    """stats 테이블 행: (champion_id, team_id, style, games, match_id, points_json)
    points 에 분 단위 순간 위치·먹은 캠프 수와 함께, 대표 경기의 정확한 이벤트(귀환·킬·오브젝트)를 담는다."""
    rows = []
    for (champ, team, style), trajs in trajectories(con, prefix).items():
        if len(trajs) < 3:
            continue
        m = medoid(trajs)
        pid = con.execute(f"""SELECT participant_id FROM {prefix}participants
                              WHERE match_id=? AND champion_id=? AND position='JUNGLE'""", [m["match_id"], champ]).fetchall()[0][0]
        payload = {"minutes": m["points"], "events": exact_events(con, prefix, m["match_id"], pid)}
        rows.append((champ, team, style, len(trajs), m["match_id"], json.dumps(payload)))
    return rows
