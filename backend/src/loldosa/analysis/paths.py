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


def build_medoids(con, prefix: str = "src.") -> list[tuple]:
    """stats 테이블 행: (champion_id, team_id, style, games, match_id, points_json)"""
    rows = []
    for (champ, team, style), trajs in trajectories(con, prefix).items():
        if len(trajs) < 3:
            continue
        m = medoid(trajs)
        rows.append((champ, team, style, len(trajs), m["match_id"], json.dumps(m["points"])))
    return rows
