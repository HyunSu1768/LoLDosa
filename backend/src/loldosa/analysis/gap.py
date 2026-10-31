"""챌린저 갭: 실제 고수(프로·챌린저·마스터+)와 플래티넘을 가르는 지표를 데이터로 찾고, 내 경기를 그 지표로 잰다.

원칙
- 지표 후보는 Match-V5 경기 결과(challenges 포함)와 타임라인에서 뽑을 수 있는 정글러 값 전부.
- '실력 지표'로 인정하려면 고수 그룹과 플래티넘을 가르는 힘(AUC)이 이긴 판끼리, 진 판끼리 따로 봐도
  같은 방향으로 남아 있어야 한다. 이기면 저절로 좋아지는 값(KDA 등)을 걸러내기 위해서다.
- 기준표(gap_reference.json)는 scripts/build_gap_reference.py 로 만들어 패키지에 넣는다.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REFERENCE_PATH = Path(__file__).resolve().parent.parent / "learn" / "gap_reference.json"


@dataclass(frozen=True)
class Feature:
    key: str
    label: str       # 화면에 보일 이름 (한국 커뮤니티 말투)
    unit: str        # 값 뒤에 붙일 단위
    concept: str     # 학습 개념 id
    drill: str       # 다음 판에서 할 구체적 연습
    fmt: str = "{:.1f}"


FEATURES: list[Feature] = [
    Feature("jcs10", "10분 정글 CS", "개", "clear-efficiency",
            "갱·싸움 끝나면 바로 리젠된 캠프부터 챙기기. 10분에 몇 개인지 매판 확인", "{:.0f}"),
    Feature("cs15", "15분 전체 CS", "개", "clear-efficiency",
            "라인이 비면 라인 CS도 먹기. 15분까지 캠프를 하나도 썩히지 않기", "{:.0f}"),
    Feature("gd10", "10분 상대 정글과 골드 차", "골드", "clear-efficiency",
            "상대 정글보다 캠프를 먼저 돌고, 손해 보는 싸움은 안 하기", "{:+.0f}"),
    Feature("xpd10", "10분 상대 정글과 경험치 차", "", "power-spikes",
            "레벨 앞설 때 먼저 싸움 걸고, 뒤질 땐 피하기", "{:+.0f}"),
    Feature("gd15", "15분 상대 정글과 골드 차", "골드", "clear-efficiency",
            "15분까지 캠프·바위게·라인을 쉬지 않고 먹기", "{:+.0f}"),
    Feature("enemy_jg_pm", "상대 정글 몬스터 처치 (분당)", "", "invading",
            "상대 정글이 반대편에 보이면 그쪽 캠프 뺏어 먹기", "{:.2f}"),
    Feature("crab_first", "첫 바위게 획득", "개", "scuttle-crab",
            "2:55 바위게 시간에 맞춰 첫 정글링 끝내기", "{:.2f}"),
    Feature("crab_total", "바위게 처치", "개", "scuttle-crab",
            "바위게가 다시 나올 때마다 주도권 있는 쪽 바위게 챙기기", "{:.1f}"),
    Feature("kp", "킬 관여율", "%", "cross-map",
            "싸움 날 것 같은 라인 근처에서 정글링하기", "{:.0%}"),
    Feature("td10", "10분 전 킬·어시", "회", "ganking",
            "3~6분에 이길 수 있는 라인 한 곳은 꼭 가 보기", "{:.1f}"),
    Feature("deaths10", "10분 전 데스", "회", "jungle-tracking",
            "상대 정글 위치를 모를 땐 상대 정글 깊이 들어가지 않기", "{:.1f}"),
    Feature("dead_pct", "죽어 있던 시간 비율", "%", "jungle-tracking",
            "불리한 싸움 피하고, 시야 없는 곳에서 혼자 걷지 않기", "{:.1%}"),
    Feature("vision_pm", "분당 시야 점수", "", "vision-control",
            "귀환할 때마다 제어 와드 사고, 오브젝트 1분 전 시야 잡기", "{:.2f}"),
    Feature("wards_pm", "분당 와드 설치", "개", "vision-control",
            "장신구 쿨마다 쓰기", "{:.2f}"),
    Feature("ward_kills_pm", "분당 와드 제거", "개", "sweeping",
            "오브젝트 전·갱 가기 전에 와드 지우기 (렌즈 쓰기)", "{:.2f}"),
    Feature("control_wards", "제어 와드 설치", "개", "vision-control",
            "귀환할 때마다 제어 와드 1개 사기", "{:.1f}"),
    Feature("unseen_recalls", "안 보이는 곳에서 귀환", "회", "recall-timing",
            "귀환은 상대 와드 없는 곳(덤불·우리 정글 안쪽)에서", "{:.1f}"),
    Feature("obj_dmg_pm", "분당 오브젝트 피해량", "", "objective-setup",
            "라인 밀렸을 때 포탑·전령·드래곤 같이 치기", "{:.0f}"),
    Feature("epic_fast", "오브젝트 나오자마자 30초 안에 처치", "회", "objective-setup",
            "오브젝트 1분 전에 먼저 자리 잡고, 나오자마자 치기", "{:.1f}"),
    Feature("epic_near_ejg", "상대 정글 옆에서 오브젝트 처치", "회", "objective-setup",
            "상대 정글 위치 보고 오브젝트 치기 (강타 싸움 피하지 않기)", "{:.1f}"),
    Feature("plates", "포탑 방패 획득", "개", "turret-plates",
            "갱 성공하면 그 라인 포탑 방패까지 같이 치기", "{:.1f}"),
    Feature("first_recall", "첫 귀환 시각", "", "recall-timing",
            "첫 정글링 끝나고 할 게 없으면 바로 귀환", "mmss"),
    Feature("gold_deaths", "1,200골드 넘게 들고 죽은 횟수", "회", "recall-timing",
            "1,200골드 모이면 싸우기 전에 귀환부터", "{:.1f}"),
    Feature("lv6_time", "6레벨 찍은 시각", "", "level-race",
            "갱 실패나 바위게 싸움으로 경험치 흘리지 않기", "mmss"),
    Feature("dmg_pm", "분당 챔피언 피해량", "", "skirmish-teamfight",
            "싸움에 늦지 않게 붙어 있기", "{:.0f}"),
    Feature("solo_kills", "솔로킬", "회", "invading",
            "레벨·아이템 앞설 때 상대 정글 캠프에서 1:1 걸기", "{:.1f}"),
    Feature("pings_pm", "분당 핑 사용", "회", "communication-pings",
            "상대 정글 위치·오브젝트 타이밍을 핑으로 알리기", "{:.2f}"),
    Feature("missing_pings", "미아 핑 (상대 사라짐)", "회", "communication-pings",
            "상대 정글·라이너가 안 보이면 바로 미아 핑", "{:.1f}"),
    Feature("omw_pings", "'가는 중' 핑", "회", "communication-pings",
            "갱·오브젝트 가기 전에 '가는 중' 핑으로 라이너 준비시키기", "{:.0f}"),
    Feature("getback_pings", "'후퇴' 핑", "회", "communication-pings",
            "상대 정글이 보이면 그쪽 라이너에게 '후퇴' 핑", "{:.1f}"),
    Feature("vision_pings", "'적 시야' 핑 (와드 위치 알림)", "회", "communication-pings",
            "상대 와드 발견하면 핑 찍고 지우기", "{:.1f}"),
]
# 상대 정글과의 차이는 같은 티어끼리 붙은 값이라 티어 비교에 못 쓴다 (마스터+ 끼리는 평균 0). 기준표 검증에서 뺀다.
# 솔로킬도 상대 실력에 달린 값이라 뺀다 (플래티넘이 오히려 더 많음: 상대가 더 쉽게 잡혀서).
RELATIVE = {"gd10", "xpd10", "gd15", "solo_kills"}
BY_KEY = {f.key: f for f in FEATURES}


def _frame(tl: dict, minute: int, pid: int) -> dict | None:
    frames = tl["info"]["frames"]
    if minute >= len(frames):
        return None
    return frames[minute]["participantFrames"].get(str(pid))


def jungler_features(match: dict, tl: dict, puuid: str) -> dict | None:
    """정글로 뛴 판의 지표 값. 정글이 아니거나 15분 전에 끝난 판은 None."""
    info = match["info"]
    me = next((p for p in info["participants"] if p["puuid"] == puuid), None)
    if not me or me.get("teamPosition") != "JUNGLE" or info["gameDuration"] < 900:
        return None
    ej = next((p for p in info["participants"] if p["teamPosition"] == "JUNGLE" and p["teamId"] != me["teamId"]), None)
    mins = info["gameDuration"] / 60
    ch = me.get("challenges", {}) or {}
    pid = me["participantId"]
    out: dict[str, float | None] = {"win": bool(me["win"]), "champion_id": me["championId"]}

    f10, f15 = _frame(tl, 10, pid), _frame(tl, 15, pid)
    out["jcs10"] = ch.get("jungleCsBefore10Minutes", f10["jungleMinionsKilled"] if f10 else None)
    out["cs15"] = (f15["minionsKilled"] + f15["jungleMinionsKilled"]) if f15 else None
    if ej:
        e10, e15 = _frame(tl, 10, ej["participantId"]), _frame(tl, 15, ej["participantId"])
        out["gd10"] = f10["totalGold"] - e10["totalGold"] if f10 and e10 else None
        out["xpd10"] = f10["xp"] - e10["xp"] if f10 and e10 else None
        out["gd15"] = f15["totalGold"] - e15["totalGold"] if f15 and e15 else None
    out["enemy_jg_pm"] = me.get("totalEnemyJungleMinionsKilled", 0) / mins
    out["crab_first"] = ch.get("initialCrabCount")
    out["crab_total"] = ch.get("scuttleCrabKills")
    out["kp"] = ch.get("killParticipation")
    out["dead_pct"] = me.get("totalTimeSpentDead", 0) / info["gameDuration"]
    out["vision_pm"] = ch.get("visionScorePerMinute", me.get("visionScore", 0) / mins)
    out["wards_pm"] = me.get("wardsPlaced", 0) / mins
    out["ward_kills_pm"] = me.get("wardsKilled", 0) / mins
    out["control_wards"] = me.get("detectorWardsPlaced", ch.get("controlWardsPlaced"))
    out["unseen_recalls"] = ch.get("unseenRecalls")
    out["obj_dmg_pm"] = me.get("damageDealtToObjectives", 0) / mins
    out["epic_fast"] = ch.get("epicMonsterKillsWithin30SecondsOfSpawn")
    out["epic_near_ejg"] = ch.get("epicMonsterKillsNearEnemyJungler")
    out["plates"] = ch.get("turretPlatesTaken")
    out["dmg_pm"] = me.get("totalDamageDealtToChampions", 0) / mins
    out["solo_kills"] = ch.get("soloKills")
    ping_keys = [k for k in me if k.endswith("Pings")]
    out["pings_pm"] = sum(me.get(k, 0) or 0 for k in ping_keys) / mins if ping_keys else None
    out["missing_pings"] = me.get("enemyMissingPings")
    out["omw_pings"] = me.get("onMyWayPings")
    out["getback_pings"] = me.get("getBackPings")
    out["vision_pings"] = me.get("enemyVisionPings")

    # 타임라인 이벤트
    td10 = d10 = 0
    lv6 = None
    purchases, kills = [], []
    for fr in tl["info"]["frames"]:
        for e in fr.get("events", []):
            t = e.get("timestamp", 0)
            ty = e.get("type")
            if ty == "CHAMPION_KILL":
                kills.append((e.get("victimId"), t))
                if t < 600_000:
                    if e.get("killerId") == pid or pid in (e.get("assistingParticipantIds") or []):
                        td10 += 1
                    if e.get("victimId") == pid:
                        d10 += 1
            elif ty == "LEVEL_UP" and e.get("participantId") == pid and e.get("level") == 6 and lv6 is None:
                lv6 = t / 1000
            elif ty == "ITEM_PURCHASED":
                purchases.append((e.get("participantId"), t))
    out["td10"], out["deaths10"], out["lv6_time"] = td10, d10, lv6

    from .turns import shop_visits

    first = next((v for v in shop_visits(purchases, kills) if v.participant_id == pid and not v.death_back), None)
    out["first_recall"] = first.ts_ms / 1000 if first else None
    gd = 0
    for victim, t in kills:
        if victim != pid or t > 20 * 60_000:
            continue
        fr = _frame(tl, int(t // 60_000), pid)
        if fr and fr.get("currentGold", 0) >= 1200:
            gd += 1
    out["gold_deaths"] = gd
    return out


# ---- 기준표 만들기 ---------------------------------------------------------------

def auc(high: list[float], low: list[float]) -> float | None:
    """고수 값이 플래티넘 값보다 클 확률 (동점 0.5). 0.5 = 못 가름."""
    if len(high) < 15 or len(low) < 15:
        return None
    import numpy as np

    h, lo = np.asarray(high, float), np.asarray(low, float)
    allv = np.concatenate([h, lo])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv))
    sv = allv[order]
    i = 0
    while i < len(sv):  # 동점 평균 순위
        j = i
        while j + 1 < len(sv) and sv[j + 1] == sv[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    r_h = ranks[: len(h)].sum()
    return float((r_h - len(h) * (len(h) + 1) / 2) / (len(h) * len(lo)))


def _q(vals: list[float], q: float) -> float:
    s = sorted(vals)
    return s[min(len(s) - 1, max(0, int(round(q * (len(s) - 1)))))]


def build_reference(groups: dict[str, list[dict]], high: tuple[str, ...], low: str,
                    min_auc: float = 0.60, min_split_auc: float = 0.56) -> dict:
    """groups: 이름 -> 지표 dict 목록. high 그룹들 vs low 그룹으로 AUC 를 재고 이긴 판/진 판 분리 검증."""
    ref = {"groups": {g: len(v) for g, v in groups.items()}, "high": list(high), "low": low, "features": {}}
    hi_rows = [r for g in high for r in groups[g]]
    lo_rows = groups[low]
    for f in FEATURES:
        if f.key in RELATIVE:
            continue

        def vals(rows, win=None):
            return [r[f.key] for r in rows if r.get(f.key) is not None and (win is None or r["win"] == win)]

        a = auc(vals(hi_rows), vals(lo_rows))
        if a is None:
            continue
        a_w, a_l = auc(vals(hi_rows, True), vals(lo_rows, True)), auc(vals(hi_rows, False), vals(lo_rows, False))
        higher_better = a >= 0.5
        strength = a if higher_better else 1 - a
        split = [x if higher_better else 1 - x for x in (a_w, a_l) if x is not None]
        validated = strength >= min_auc and len(split) == 2 and min(split) >= min_split_auc
        hv = vals(hi_rows)
        thr = _q(hv, 0.25) if higher_better else _q(hv, 0.75)
        if higher_better and thr <= 0:  # 고수 하위 25%도 0이면 기준이 의미 없어서 중앙값을 쓴다
            thr = _q(hv, 0.5)

        def pass_rate(rows):
            v = vals(rows)
            return round(sum((x >= thr) if higher_better else (x <= thr) for x in v) / len(v), 3) if v else None

        ref["features"][f.key] = {
            "threshold": thr, "pass": {g: pass_rate(rows) for g, rows in groups.items()},
            "auc": round(strength, 3), "auc_win": round(split[0], 3) if split else None,
            "auc_loss": round(split[1], 3) if len(split) > 1 else None,
            "higher_better": higher_better, "validated": validated,
            "groups": {g: {"n": len(vals(rows)), "median": round(_q(vals(rows), 0.5), 3),
                           "p25": round(_q(vals(rows), 0.25), 3), "p75": round(_q(vals(rows), 0.75), 3)}
                       for g, rows in groups.items() if len(vals(rows)) >= 10},
        }
    # 챔피언 보정: 마스터+ 에서 챔피언별 중앙값이 전체 중앙값과 얼마나 다른지 (15판 이상인 챔피언만)
    base_rows = groups.get("apex") or hi_rows
    ref["champ_offset"] = {}
    for key, r in ref["features"].items():
        if not r["validated"]:
            continue
        allv = [x[key] for x in base_rows if x.get(key) is not None]
        if not allv:
            continue
        overall = _q(allv, 0.5)
        by: dict[int, list] = {}
        for x in base_rows:
            if x.get(key) is not None:
                by.setdefault(x["champion_id"], []).append(x[key])
        ref["champ_offset"][key] = {str(c): round(_q(v, 0.5) - overall, 4) for c, v in by.items() if len(v) >= 15}
    return ref


def champ_adjust(row: dict, key: str, ref: dict) -> float | None:
    """챔피언 특성 빼기: 이 챔피언 고수들이 원래 높거나 낮은 만큼 보정한 값."""
    v = row.get(key)
    if v is None:
        return None
    off = (ref.get("champ_offset", {}).get(key) or {}).get(str(row.get("champion_id")), 0.0)
    return v - off


# ---- 내 경기 진단 ------------------------------------------------------------------

def load_reference(path: Path = REFERENCE_PATH) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def fmt_value(f: Feature, v: float | None) -> str:
    if v is None:
        return "-"
    if f.fmt == "mmss":
        v = int(round(v))
        return f"{v // 60}:{v % 60:02d}"
    text = f"{int(v)}" if f.fmt == "{:.1f}" and float(v).is_integer() else f.fmt.format(v)
    return text + ("" if f.unit in ("%", "") else f.unit)


def personal_gap(rows: list[dict], ref: dict, target: str = "challenger", limit: int = 3) -> dict:
    """내 최근 경기 지표 중앙값을 플래티넘·고수 분포와 비교해, 챌린저까지 가장 큰 차이를 순서대로.

    우선순위 = 가르는 힘(AUC-0.5) × 목표까지 남은 거리(플래티넘~목표 간격 기준). 이미 목표 이상이면 강점."""
    items = []
    for key, r in ref["features"].items():
        if not r["validated"] or key not in BY_KEY:
            continue
        f = BY_KEY[key]
        vals = [champ_adjust(x, key, ref) for x in rows if x.get(key) is not None]
        if len(vals) < 3:
            continue
        mine = _q(vals, 0.5)
        g = r["groups"]
        tgt = g.get(target) or g.get("pro") or g.get("apex")
        base = g.get(ref["low"])
        if not tgt or not base:
            continue
        span = abs(tgt["median"] - base["median"]) or 1e-9
        sign = 1 if r["higher_better"] else -1
        short = (tgt["median"] - mine) * sign / span  # 1 = 플래티넘 수준만큼 모자람, 0 이하 = 목표 도달
        items.append({
            "key": key, "label": f.label, "concept": f.concept, "drill": f.drill,
            "mine": round(mine, 3), "mine_text": fmt_value(f, mine), "games": len(vals),
            "target": tgt["median"], "target_text": fmt_value(f, tgt["median"]),
            "platinum_text": fmt_value(f, base["median"]),
            "groups_text": {k: fmt_value(f, v["median"]) for k, v in g.items()},
            "auc": r["auc"], "short": round(short, 2), "priority": round(max(short, 0) * (r["auc"] - 0.5), 4),
            "examples": [{**e, "value_text": fmt_value(f, e["value"])} for e in (ref.get("exemplars", {}).get(key) or [])[:3]],
            # 한 번에 챌린저까지는 무리라서, 남은 거리의 1/3씩 끊어서 '이번 주 목표'로
            "step_text": fmt_value(f, mine + (tgt["median"] - mine) / 3),
        })
    # 진행도: 지표마다 플래티넘 중앙값=0, 목표 중앙값=100 으로 놓고 가르는 힘(AUC)으로 가중 평균
    w = sum(x["auc"] - 0.5 for x in items)
    progress = round(sum((x["auc"] - 0.5) * min(max(1 - x["short"], 0), 1.2) for x in items) / w * 100) if w else None
    gaps = sorted([x for x in items if x["short"] > 0.15], key=lambda x: -x["priority"])
    strengths = sorted([x for x in items if x["short"] <= 0.1], key=lambda x: -x["auc"])
    return {"target": target, "games": len(rows), "progress": progress, "gaps": gaps[:limit], "all": sorted(items, key=lambda x: -x["priority"]),
            "strengths": strengths[:3]}


def game_gap(feat: dict, ref: dict) -> list[dict]:
    """한 판의 검증된 지표를 고수 기준선(threshold)·플래티넘·챌린저 중앙값과 나란히."""
    out = []
    for key, r in sorted(ref["features"].items(), key=lambda kv: -kv[1]["auc"]):
        if not r["validated"] or key not in BY_KEY or feat.get(key) is None:
            continue
        f, v, g = BY_KEY[key], feat[key], r["groups"]
        adj = champ_adjust(feat, key, ref)  # 판정은 챔피언 특성을 뺀 값으로
        ok = adj >= r["threshold"] if r["higher_better"] else adj <= r["threshold"]
        out.append({"key": key, "label": f.label, "concept": f.concept, "mine_text": fmt_value(f, v), "ok": ok,
                    "threshold_text": fmt_value(f, r["threshold"]), "higher_better": r["higher_better"],
                    "platinum_text": fmt_value(f, g[ref["low"]]["median"]) if ref["low"] in g else "-",
                    "challenger_text": fmt_value(f, (g.get("challenger") or g.get("apex"))["median"]),
                    "auc": r["auc"], "drill": f.drill})
    return out
