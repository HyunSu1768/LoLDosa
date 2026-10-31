"""목표 체크: 경기 리뷰에서 측정한 값으로 개념별 '했다/못했다'를 판정한다.

학습 루프의 핵심. 연습 목표(개념)를 정하면 브리핑에서 상기시키고, 경기 후 이 체크로 달성 여부를 기록한다.
기준은 고티어 통계(리뷰가 함께 담아온 값)나 리서치에서 나온 원칙을 쓴다. 측정할 수 없으면 'na'.
"""

from __future__ import annotations


def _mmss(sec: float | None) -> str:
    if sec is None:
        return "-"
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


# id → (보여줄 목표 문장, 판정 함수(facts) -> (status, 측정값 문장))
def _full_clear(f):
    """고티어에서 이 챔피언이 주로 풀클리어(40% 이상)하면 6캠프, 아니면 4캠프가 목표."""
    c = f.get("camps3")
    if c is None:
        return "na", "-"
    target = 6 if (f.get("full_clear_rate") or 0) >= 0.4 else 4
    return ("pass" if c >= target else "fail"), f"3:00까지 {c}캠프 (이 챔피언 목표 {target}캠프)"


def _clear_eff(f):
    cs, b = f.get("cs10"), f.get("cs10_bench")
    if cs is None or not b:
        return "na", "-"
    return ("pass" if cs >= 0.9 * b else "fail"), f"10분 정글 CS {cs} (고티어 {b:.0f})"


def _turn(f):
    t = (f.get("obj_turns") or {}).get("DRAGON")
    if not t:
        return "na", "20분 전에 드래곤 안 잡힘"
    label = {"sync": "라이너와 같이 미리 귀환", "jg_only": "미리 귀환", "none": "미리 귀환 안 함",
             "late": "직전 30초 안에 귀환"}[t["turn"]]
    return ("pass" if t["turn"] in ("sync", "jg_only") else "fail"), f"첫 드래곤 전: {label}"


def _recall(f):
    """검증 결과 티어를 가른 두 가지만 본다: 1,200골드 넘게 들고 죽기, 첫 귀환 5:00 넘기기.
    (오브젝트 직전 귀환은 프로 8%·챌린저 15%·플래티넘 14%로 차이가 없어서 뺐다)"""
    fr = f.get("first_recall_s")
    if f.get("gold_death"):
        return "fail", f"골드 {f['gold_death']:,} 들고 죽음"
    if fr is None:
        return "na", "-"
    if fr > 300:
        return "fail", f"첫 귀환 {_mmss(fr)} (5:00 넘김)"
    return "pass", f"첫 귀환 {_mmss(fr)}, 골드 들고 안 죽음"


def _objective(f):
    turns = f.get("obj_turns") or {}
    if not turns and "far_lost" not in f and "traded" not in f:
        return "na", "-"
    far = f.get("far_lost", 0)
    late = sum(1 for t in turns.values() if t["turn"] == "late")
    ok = far == 0 and late == 0
    traded = f.get("traded", 0)
    return ("pass" if ok else "fail"), f"맞교환 없이 내준 오브젝트 {far}회, 맞교환 {traded}회, 직전 귀환 {late}회"


def _tracking(f):
    if "risky_deaths10" not in f:
        return "na", "-"
    n = f["risky_deaths10"]
    return ("pass" if n == 0 else "fail"), f"10분 전 상대 정글·강가 데스 {n}회"


def _counter(f):
    if "enemy_ganks10" not in f and "deaths10" not in f:
        return "na", "-"
    n = f.get("enemy_ganks10", 0)
    return ("pass" if n == 0 else "fail"), f"10분 전 상대 정글 갱에 아군이 죽은 횟수 {n}회"


def _vision(f):
    v, b = f.get("vision_pm"), f.get("vision_bench")
    if v is None or not b:
        return "na", "-"
    return ("pass" if v >= 0.9 * b else "fail"), f"분당 시야 {v:.2f} (고티어 {b:.2f})"


def _power(f):
    if "camps3" not in f:
        return "na", "-"
    return ("fail" if f.get("bad_band_fight") else "pass"), (
        "레벨 불리할 때 정글 싸움에서 짐" if f.get("bad_band_fight") else "레벨 불리할 때 정글 싸움에서 안 짐")


CHECKS = {
    "full-clear": ("3:00까지 목표 캠프 수 먹기 (풀캠 챔피언 6캠프, 아니면 4캠프)", _full_clear),
    "clear-efficiency": ("10분 정글 CS 고티어 평균의 90% 이상", _clear_eff),
    "turn-tempo": ("첫 드래곤 잡히기 0:40~2:30 전에 미리 귀환", _turn),
    "recall-timing": ("첫 귀환은 5:00 전에, 1,200골드 넘게 들고 죽지 않기", _recall),
    "objective-setup": ("오브젝트 싸움에 합류하기", _objective),
    "jungle-tracking": ("10분 전 상대 정글·강가에서 죽지 않기", _tracking),
    "counter-gank": ("10분 전 상대 정글 갱에 아군 안 죽게 하기", _counter),
    "vision-control": ("분당 시야 점수 고티어 평균의 90% 이상", _vision),
    "power-spikes": ("레벨이 불리할 땐 정글 싸움 피하기", _power),
}


# ---- 챌린저 갭 기준표에서 온 체크 (analysis/gap.py, learn/gap_reference.json) ----------------------------
# 개념 하나에 지표 하나. 기준선 = 고수(프로·챌린저·마스터+) 하위 25%. 기준표에서 검증된 것만 채점한다.
GAP_CHECKS = {
    "communication-pings": "missing_pings",
    "cross-map": "kp",
    "level-race": "lv6_time",
    "sweeping": "ward_kills_pm",
    "jungle-tracking": "dead_pct",
}


def _gap_ref():
    from ..analysis.gap import load_reference

    global _REF
    try:
        return _REF
    except NameError:
        _REF = load_reference()
        return _REF


def _gap_check(key):
    def fn(f):
        from ..analysis.gap import BY_KEY, fmt_value

        ref = _gap_ref()
        r = ref and ref["features"].get(key)
        if not r or f.get(key) is None:
            return "na", "-"
        from ..analysis.gap import champ_adjust

        v, ft = f[key], BY_KEY[key]
        adj = champ_adjust(f, key, ref)  # 챔피언 특성 보정 후 판정
        ok = adj >= r["threshold"] if r["higher_better"] else adj <= r["threshold"]
        return ("pass" if ok else "fail"), f"{ft.label} {fmt_value(ft, v)} (고수 기준 {fmt_value(ft, r['threshold'])})"
    return fn


def _gap_goal(key):
    from ..analysis.gap import BY_KEY, fmt_value

    ref = _gap_ref()
    r = ref and ref["features"].get(key)
    ft = BY_KEY[key]
    if not r:
        return ft.label
    return f"{ft.label} {fmt_value(ft, r['threshold'])} {'이상' if r['higher_better'] else '이하'} (고수 4명 중 3명이 넘는 선)"


for _cid, _key in GAP_CHECKS.items():
    CHECKS[_cid] = (_gap_goal(_key), _gap_check(_key))

# 실제 경기 검증 (research_notes/검증/검증 결과.md): 프로 12명 120판·챌린저 8명 96판·플래티넘 35명 217판.
# 통과율이 고수 그룹에서 확실히 높은 체크만 채점한다. 나머지는 값만 '참고'로 보여주고 달성률·숙련도엔 안 넣는다.
VALIDATION = {  # concept: (프로, 챌린저, 플래티넘 통과율, 채점 여부)
    # 플래티넘 값은 두 표본(63판 + 새로 받은 154판) 합계. 두 표본 모두 같은 방향으로 재현됐다.
    "full-clear": (0.64, 0.76, 0.42, True),
    "clear-efficiency": (0.83, 0.94, 0.41, True),
    "vision-control": (0.78, 0.67, 0.42, True),
    "recall-timing": (0.57, 0.60, 0.33, True),
    "objective-setup": (0.67, 0.54, 0.51, False),
    "turn-tempo": (0.44, 0.41, 0.38, False),
    "counter-gank": (0.20, 0.23, 0.11, False),
    "power-spikes": (0.90, 0.97, 0.91, False),
}
for _cid, _key in GAP_CHECKS.items():
    _r = (_gap_ref() or {}).get("features", {}).get(_key)
    if _r:
        _p = _r["pass"]
        VALIDATION[_cid] = (_p.get("pro"), _p.get("challenger"), _p.get("platinum"), _r["validated"])
GRADED = {k for k, v in VALIDATION.items() if v[3]}


def evaluate(facts: dict) -> list[dict]:
    """채점하는 체크는 pass/fail, 검증에서 티어를 못 가른 체크는 status 'na' + info(측정값)로 돌려준다."""
    out = []
    for cid, (goal, fn) in CHECKS.items():
        status, value = fn(facts)
        v = VALIDATION.get(cid)
        item = {"concept": cid, "goal": goal, "status": status, "value": value, "graded": cid in GRADED,
                "validation": {"pro": v[0], "challenger": v[1], "platinum": v[2]} if v else None}
        if cid not in GRADED:
            item["info"] = value if status != "na" else None
            item["status"] = "na"
        out.append(item)
    return out
