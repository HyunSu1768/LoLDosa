"""개념 체크: 경기 리뷰에서 측정한 값으로 개념별 '했다/못했다'를 판정한다.

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
    return ("pass" if c >= target else "fail"), f"3:00 {c}캠프 (이 챔피언 목표 {target}캠프)"


def _clear_eff(f):
    cs, b = f.get("cs10"), f.get("cs10_bench")
    if cs is None or not b:
        return "na", "-"
    return ("pass" if cs >= 0.9 * b else "fail"), f"10분 정글 CS {cs} (고티어 {b:.0f})"


def _turn(f):
    t = (f.get("obj_turns") or {}).get("DRAGON")
    if not t:
        return "na", "20분 전 드래곤 없음"
    label = {"sync": "라이너와 같이 미리 귀환", "jg_only": "미리 귀환", "none": "미리 귀환 안 함",
             "late": "직전 30초에 귀환"}[t["turn"]]
    return ("pass" if t["turn"] in ("sync", "jg_only") else "fail"), f"첫 드래곤 전: {label}"


def _recall(f):
    turns = f.get("obj_turns") or {}
    if any(t["turn"] == "late" for t in turns.values()):
        return "fail", "오브젝트 직전에 귀환"
    if f.get("gold_death"):
        return "fail", f"골드 {f['gold_death']:,} 들고 사망"
    if f.get("first_recall_s") is None and not turns:
        return "na", "-"
    return "pass", f"첫 귀환 {_mmss(f.get('first_recall_s'))}, 직전 귀환·골드 사망 없음"


def _objective(f):
    turns = f.get("obj_turns") or {}
    if not turns and "far_lost" not in f:
        return "na", "-"
    far = f.get("far_lost", 0)
    late = sum(1 for t in turns.values() if t["turn"] == "late")
    ok = far == 0 and late == 0
    return ("pass" if ok else "fail"), f"멀리서 내준 오브젝트 {far}회, 직전 귀환 {late}회"


def _tracking(f):
    if "risky_deaths10" not in f:
        return "na", "-"
    n = f["risky_deaths10"]
    return ("pass" if n == 0 else "fail"), f"10분 전 상대 정글·강가 데스 {n}회"


def _counter(f):
    if "enemy_ganks10" not in f and "deaths10" not in f:
        return "na", "-"
    n = f.get("enemy_ganks10", 0)
    return ("pass" if n == 0 else "fail"), f"10분 전 적 정글 갱으로 아군 사망 {n}회"


def _vision(f):
    v, b = f.get("vision_pm"), f.get("vision_bench")
    if v is None or not b:
        return "na", "-"
    return ("pass" if v >= 0.9 * b else "fail"), f"분당 시야 {v:.2f} (고티어 {b:.2f})"


def _power(f):
    if "camps3" not in f:
        return "na", "-"
    return ("fail" if f.get("bad_band_fight") else "pass"), (
        "불리한 레벨 구간에서 정글 교전 패배" if f.get("bad_band_fight") else "불리한 레벨 구간 교전 패배 없음")


CHECKS = {
    "full-clear": ("3:00까지 챔피언 기준 클리어 완료 (풀클 위주 챔피언 6캠프, 아니면 4캠프)", _full_clear),
    "clear-efficiency": ("10분 정글 CS 고티어 평균의 90% 이상", _clear_eff),
    "turn-tempo": ("첫 드래곤 0:40~2:30 전에 미리 귀환", _turn),
    "recall-timing": ("오브젝트 직전 귀환 금지, 1,200골드 이상 들고 죽지 않기", _recall),
    "objective-setup": ("오브젝트를 멀리서 내주지 않기", _objective),
    "jungle-tracking": ("10분 전 상대 정글·강가에서 죽지 않기", _tracking),
    "counter-gank": ("10분 전 적 정글 갱으로 아군을 잃지 않기", _counter),
    "vision-control": ("분당 시야 점수 고티어 평균의 90% 이상", _vision),
    "power-spikes": ("불리한 레벨 구간에서 정글 교전 피하기", _power),
}


def evaluate(facts: dict) -> list[dict]:
    out = []
    for cid, (goal, fn) in CHECKS.items():
        status, value = fn(facts)
        out.append({"concept": cid, "goal": goal, "status": status, "value": value})
    return out
