"""판단 훈련: '그 순간'의 상황 → 다음 1분의 행동 → 2분 뒤 결과.

고티어 정글러의 매 분(2~20분) 상황을 기록해 두고, 내 경기의 판단 지점과 비슷한 상황에서
고티어 정글러들이 무엇을 했고 그 결과가 어땠는지를 보여준다.

관측 한계
- 위치는 1분 간격 스냅샷이다. '행동'은 다음 1분 동안의 이벤트(상점 구매·킬·오브젝트)와
  1분 뒤 위치로 분류한다. 킬이 나지 않은 갱 시도는 '그 라인으로 이동'으로만 보인다.
- 결과는 상관관계다. 같은 행동이라도 실행에 따라 결과가 다르다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .geometry import map_side, relative_region
from .turns import shop_visits

MINUTES = range(2, 21)

ACTIONS = ["recall", "objective", "gank_top", "gank_mid", "gank_bot", "invade", "river", "farm"]
ACTION_KO = {
    "recall": "귀환해서 정비", "objective": "오브젝트 치기", "gank_top": "탑 갱", "gank_mid": "미드 갱",
    "gank_bot": "봇 갱", "invade": "카정 (상대 정글)", "river": "강가로 (바위게·시야)", "farm": "내 정글 파밍",
}
ACTION_CONCEPTS = {
    "recall": ["recall-timing", "turn-tempo"], "objective": ["objective-setup", "dragon"],
    "gank_top": ["ganking", "lane-priority"], "gank_mid": ["ganking", "lane-priority"],
    "gank_bot": ["ganking", "lane-priority"], "invade": ["invading", "jungle-tracking"],
    "river": ["scuttle-crab", "vision-control"], "farm": ["clear-efficiency", "jungle-pathing"],
}

# 오브젝트 타이머 (2026: 드래곤 5:00·재생성 5분, 유충 8:00·14:45 사라짐, 전령 15:00~19:45, 바론 20:00·재생성 6분)
DRAGON_FIRST, DRAGON_RESPAWN = 300, 300
GRUB_SPAWN, GRUB_END = 480, 885
HERALD_SPAWN, HERALD_END = 900, 1185
BARON_FIRST = 1200

FEATURES = ["minute", "hp", "gold", "level_diff", "gold_diff", "lane_top", "lane_mid", "lane_bot",
            "to_dragon", "to_grub", "to_herald", "dragon_diff", "side_top", "enemy_side_top",
            "r_own", "r_enemy", "r_river", "r_lane", "r_base"]
# 거리 계산 가중치 (스케일 정규화 후)
WEIGHTS = np.array([2.0, 1.0, 1.0, 1.0, 1.0, 0.7, 0.7, 0.7, 1.5, 1.0, 0.7, 0.7, 0.8, 0.8,
                    0.8, 0.8, 0.8, 0.8, 1.0])
SCALES = np.array([1.0, 0.25, 600.0, 1.0, 600.0, 800.0, 800.0, 1000.0, 120.0, 120.0, 120.0, 1.0, 1.0, 1.0,
                   1.0, 1.0, 1.0, 1.0, 1.0])


@dataclass
class MatchData:
    """한 경기의 정규화된 데이터 (store 의 participants/frames/events 에서)."""
    match_id: str
    parts: dict  # pid -> {team, position, champion_id, puuid}
    frames: dict  # (pid, minute) -> {x, y, level, gold, jcs, cur, hp, hp_max}
    events: list  # dict(ts_ms, type, participant_id, victim_id, assists, team_id, monster_type, x, y)
    purchases: list  # (pid, ts_ms)


def load_match(con, match_id: str, prefix: str = "") -> MatchData:
    """prefix: 분석 빌드에서 ATTACH 한 DB 이름 (예: 'src.')."""
    parts = {pid: {"team": team, "position": pos, "champion_id": champ, "puuid": puuid}
             for pid, team, pos, champ, puuid in con.execute(
                 f"SELECT participant_id, team_id, position, champion_id, puuid FROM {prefix}participants WHERE match_id=?",
                 [match_id]).fetchall()}
    frames = {}
    for pid, m, x, y, lvl, gold, jcs, cur, hp, hpm in con.execute(
            "SELECT participant_id, minute, x, y, level, total_gold, jungle_cs, current_gold, hp, hp_max "
            f"FROM {prefix}frames WHERE match_id=?", [match_id]).fetchall():
        frames[(pid, m)] = {"x": x, "y": y, "level": lvl, "gold": gold, "jcs": jcs, "cur": cur, "hp": hp, "hp_max": hp_max_or(hpm)}
    ev = [dict(zip(["ts_ms", "type", "participant_id", "victim_id", "assists", "team_id", "monster_type", "x", "y"], r))
          for r in con.execute(
              f"SELECT ts_ms, type, participant_id, victim_id, assists, team_id, monster_type, x, y FROM {prefix}events "
              "WHERE match_id=? AND type IN ('CHAMPION_KILL', 'ELITE_MONSTER_KILL') ORDER BY ts_ms", [match_id]).fetchall()]
    purchases = con.execute(f"SELECT participant_id, ts_ms FROM {prefix}events WHERE match_id=? AND type='ITEM_PURCHASED'",
                            [match_id]).fetchall()
    return MatchData(match_id, parts, frames, ev, purchases)


def hp_max_or(v):
    return v if v else None


def _objective_clock(events: list, team: int, t: float) -> dict:
    """t(초) 시점의 오브젝트 상태: 다음 드래곤까지 남은 초 등."""
    dragons = [e for e in events if e["type"] == "ELITE_MONSTER_KILL" and e["monster_type"] == "DRAGON" and e["ts_ms"] / 1000 <= t]
    next_dragon = (dragons[-1]["ts_ms"] / 1000 + DRAGON_RESPAWN) if dragons else DRAGON_FIRST
    grubs_taken = sum(1 for e in events if e["type"] == "ELITE_MONSTER_KILL" and e["monster_type"] == "HORDE" and e["ts_ms"] / 1000 <= t)
    herald_taken = any(e["type"] == "ELITE_MONSTER_KILL" and e["monster_type"] == "RIFTHERALD" and e["ts_ms"] / 1000 <= t
                       for e in events)
    ours = sum(1 for e in dragons if e["team_id"] == team)
    return {
        "to_dragon": max(0.0, next_dragon - t),
        "to_grub": (max(0.0, GRUB_SPAWN - t) if grubs_taken < 3 and t < GRUB_END else 999.0),
        "to_herald": (max(0.0, HERALD_SPAWN - t) if not herald_taken and t < HERALD_END else 999.0),
        "dragon_diff": ours - (len(dragons) - ours),
    }


def _involved(e, pid):
    return e["participant_id"] == pid or pid in (e["assists"] or [])


def jungler_states(md: MatchData) -> list[dict]:
    """경기의 두 정글러에 대해 분마다 (상황, 다음 1분 행동, 2분 뒤 결과)."""
    out = []
    jgs = [pid for pid, p in md.parts.items() if p["position"] == "JUNGLE"]
    if len(jgs) != 2:
        return out
    visits = shop_visits(md.purchases, [(e["victim_id"], e["ts_ms"]) for e in md.events if e["type"] == "CHAMPION_KILL"])
    for pid in jgs:
        me = md.parts[pid]
        team = me["team"]
        epid = next(j for j in jgs if j != pid)
        allies = [q for q, p in md.parts.items() if p["team"] == team]
        enemies = [q for q, p in md.parts.items() if p["team"] != team]
        for m in MINUTES:
            f, ef = md.frames.get((pid, m)), md.frames.get((epid, m))
            f1 = md.frames.get((pid, m + 1))
            if not f or not ef or not f1 or f["x"] is None:
                continue
            t = m * 60.0
            st = state_vector(md, pid, epid, team, m)
            act = classify_action(md, pid, team, m, visits)
            out.append({"pid": pid, "team": team, "champ": me["champion_id"], "minute": m, **st,
                        "action": act, **outcome(md, pid, team, allies, enemies, m)})
    return out


def lane_diff(md: MatchData, team: int, m: int, positions: tuple[str, ...]) -> float:
    mine = sum((md.frames.get((q, m)) or {}).get("gold") or 0 for q, p in md.parts.items()
               if p["team"] == team and p["position"] in positions)
    theirs = sum((md.frames.get((q, m)) or {}).get("gold") or 0 for q, p in md.parts.items()
                 if p["team"] != team and p["position"] in positions)
    return float(mine - theirs)


def state_vector(md: MatchData, pid: int, epid: int, team: int, m: int) -> dict:
    f, ef = md.frames[(pid, m)], md.frames[(epid, m)]
    reg = relative_region(team, f["x"], f["y"])
    clock = _objective_clock(md.events, team, m * 60.0)
    hp = (f["hp"] / f["hp_max"]) if f.get("hp") is not None and f.get("hp_max") else 1.0
    return {
        "hp": hp, "gold": float(f.get("cur") or 0), "level_diff": float((f["level"] or 0) - (ef["level"] or 0)),
        "gold_diff": float((f["gold"] or 0) - (ef["gold"] or 0)),
        "lane_top": lane_diff(md, team, m, ("TOP",)), "lane_mid": lane_diff(md, team, m, ("MIDDLE",)),
        "lane_bot": lane_diff(md, team, m, ("BOTTOM", "UTILITY")),
        **clock,
        "side_top": 1.0 if map_side(f["x"], f["y"]) == "top" else 0.0,
        "enemy_side_top": 1.0 if ef["x"] is not None and map_side(ef["x"], ef["y"]) == "top" else 0.0,
        "region": reg,
    }


def classify_action(md: MatchData, pid: int, team: int, m: int, visits) -> str:
    t0, t1 = m * 60_000, (m + 1) * 60_000
    if any(v.participant_id == pid and not v.death_back and t0 < v.ts_ms <= t1 for v in visits):
        return "recall"
    for e in md.events:
        if not t0 < e["ts_ms"] <= t1 + 30_000:
            continue
        if e["type"] == "ELITE_MONSTER_KILL" and e["team_id"] == team:
            f = md.frames.get((pid, m + 1))
            if e["participant_id"] == pid or (f and f["x"] is not None and math.dist((f["x"], f["y"]), (e["x"], e["y"])) < 3000):
                return "objective"
    f1 = md.frames.get((pid, m + 1))
    reg1 = relative_region(team, f1["x"], f1["y"]) if f1 and f1["x"] is not None else "unknown"
    lane_kill = next((e for e in md.events if e["type"] == "CHAMPION_KILL" and t0 < e["ts_ms"] <= t1
                      and _involved(e, pid) and relative_region(team, e["x"], e["y"]) in ("top", "mid", "bot")), None)
    if lane_kill:
        return "gank_" + relative_region(team, lane_kill["x"], lane_kill["y"])
    if reg1 in ("top", "mid", "bot"):
        return "gank_" + reg1
    if reg1 == "enemy_jungle":
        return "invade"
    if reg1 == "river":
        return "river"
    return "farm"


def outcome(md: MatchData, pid: int, team: int, allies, enemies, m: int) -> dict:
    def team_gold(ids, mm):
        return sum((md.frames.get((q, mm)) or {}).get("gold") or 0 for q in ids)

    m2 = m + 2
    have = all((q, m2) in md.frames for q in allies + enemies)
    swing = ((team_gold(allies, m2) - team_gold(enemies, m2)) - (team_gold(allies, m) - team_gold(enemies, m))) if have else None
    t0, t2 = m * 60_000, (m + 2) * 60_000
    died = any(e["type"] == "CHAMPION_KILL" and e["victim_id"] == pid and t0 < e["ts_ms"] <= t2 for e in md.events)
    obj = sum((1 if e["team_id"] == team else -1) for e in md.events
              if e["type"] == "ELITE_MONSTER_KILL" and t0 < e["ts_ms"] <= t2)
    return {"swing": swing, "died": died, "obj": obj}


REGION_FEATURES = {"r_own": ("own_jungle",), "r_enemy": ("enemy_jungle",), "r_river": ("river",),
                   "r_lane": ("top", "mid", "bot"), "r_base": ("base",)}


def to_vector(st: dict) -> np.ndarray:
    row = []
    for k in FEATURES:
        if k in REGION_FEATURES:
            row.append(1.0 if st.get("region") in REGION_FEATURES[k] else 0.0)
        elif k in ("to_dragon", "to_grub", "to_herald"):
            row.append(min(float(st[k]), 360.0))
        else:
            row.append(float(st[k]))
    return np.array(row)


def similar(pool: list[dict], st: dict, k: int = 60) -> list[dict]:
    """같은 시간대(±1분) 고티어 상황 중 가장 비슷한 k 개."""
    cand = [r for r in pool if abs(r["minute"] - st["minute"]) <= 1]
    if not cand:
        return []
    X = np.stack([to_vector(r) for r in cand]) / SCALES
    q = to_vector(st) / SCALES
    d = np.sqrt((((X - q) ** 2) * WEIGHTS).sum(axis=1))
    idx = np.argsort(d)[:k]
    return [dict(cand[i], _dist=float(d[i])) for i in idx]


def summarize(neigh: list[dict]) -> list[dict]:
    """이웃들의 행동 분포와 행동별 결과."""
    n = len(neigh)
    out = []
    for a in ACTIONS:
        rows = [r for r in neigh if r["action"] == a]
        if not rows:
            continue
        sw = [r["swing"] for r in rows if r["swing"] is not None]
        out.append({"action": a, "label": ACTION_KO[a], "n": len(rows), "share": len(rows) / n,
                    "swing": (sum(sw) / len(sw)) if sw else None,
                    "died": sum(r["died"] for r in rows) / len(rows),
                    "obj": sum(r["obj"] for r in rows) / len(rows)})
    return sorted(out, key=lambda x: -x["share"])


STATE_COLUMNS = ["bucket", "patch", "match_id", "pid", "champ", "minute", "hp", "gold", "level_diff", "gold_diff",
                 "lane_top", "lane_mid", "lane_bot", "to_dragon", "to_grub", "to_herald", "dragon_diff", "side_top",
                 "enemy_side_top", "region", "action", "swing", "died", "obj"]


def build_states(con, prefix: str = "src.") -> list[tuple]:
    """분석 빌드용: 모든 경기의 정글러 상황 행."""
    rows = []
    for mid, bucket, patch in con.execute(f"SELECT match_id, bucket, patch FROM {prefix}matches").fetchall():
        md = load_match(con, mid, prefix)
        for r in jungler_states(md):
            r = dict(r, bucket=bucket, patch=patch, match_id=mid)
            rows.append(tuple(r.get(c) for c in STATE_COLUMNS))
    return rows
