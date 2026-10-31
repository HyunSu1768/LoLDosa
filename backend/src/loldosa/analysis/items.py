"""골드를 아이템으로 말하기: '423골드 앞서요'는 감이 안 와서 '롱소드 1개쯤 앞서요'로 바꾼다.

가격은 Data Dragon 최신 패치 item.json (없으면 2026 시즌 값으로 대체).
기준 아이템: 롱소드(1036), B.F. 대검(1038), 완성 아이템(전설 아이템 평균 가격).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

LONG_SWORD, BF_SWORD = 1036, 1038
FALLBACK = {"long": 350, "bf": 1300, "legend": 3000}


@lru_cache(maxsize=4)
def prices(data_dir: str | None = None, locale: str = "ko_KR") -> dict:
    """{'long': 350, 'bf': 1300, 'legend': 3000(전설 아이템 평균, 100단위 반올림)}"""
    if data_dir:
        root = Path(data_dir) / "ddragon"
        files = sorted(root.glob(f"*/item.{locale}.json"), key=lambda p: [int(x) for x in p.parent.name.split(".") if x.isdigit()])
        if files:
            d = json.loads(files[-1].read_text(encoding="utf-8"))["data"]
            leg = [v["gold"]["total"] for v in d.values()
                   if v.get("gold", {}).get("purchasable") and not v.get("into") and v["gold"]["total"] >= 2500
                   and (v.get("maps") or {}).get("11", True)]
            return {"long": d.get(str(LONG_SWORD), {}).get("gold", {}).get("total", FALLBACK["long"]),
                    "bf": d.get(str(BF_SWORD), {}).get("gold", {}).get("total", FALLBACK["bf"]),
                    "legend": int(round(sum(leg) / len(leg), -2)) if leg else FALLBACK["legend"]}
    return dict(FALLBACK)


def gold_as_items(gold: float, p: dict | None = None) -> dict:
    """골드 양 → {'text': '롱소드 2개쯤', 'item': 1036, 'count': 2}. 150골드 미만이면 '거의 같아요'."""
    p = p or FALLBACK
    g = abs(gold or 0)
    if g < 150:
        return {"text": "거의 같아요", "item": None, "count": 0}
    if g < p["bf"] * 0.75:  # ~975골드까지는 롱소드 개수로
        n = max(1, round(g / p["long"]))
        return {"text": f"롱소드 {n}개쯤", "item": LONG_SWORD, "count": n}
    if g < p["legend"] * 0.8:  # 2,400골드까지는 B.F. 대검
        n = max(1.0, round(g / p["bf"] * 2) / 2)  # 0.5개 단위
        return {"text": f"B.F. 대검 {_count(n)}쯤", "item": BF_SWORD, "count": n}
    n = max(1.0, round(g / p["legend"] * 2) / 2)
    return {"text": f"완성 아이템 {_count(n)}쯤", "item": None, "count": n}


def _count(n: float) -> str:
    return f"{int(n)}개 반" if n % 1 else f"{int(n)}개"


def gold_diff_say(diff: float, p: dict | None = None, us: str = "우리") -> str:
    """+면 '우리가 롱소드 1개쯤 앞서요', -면 '우리가 롱소드 1개쯤 밀려요'."""
    it = gold_as_items(diff, p)
    if not it["count"]:
        return "거의 같아요"
    return f"{us}가 {it['text']} {'앞서요' if diff > 0 else '밀려요'}"


def can_buy(gold: float, p: dict | None = None) -> str:
    """가진 골드 → '롱소드 2개를 살 수 있어요' 같은 말."""
    p = p or FALLBACK
    if gold >= p["bf"]:
        return f"B.F. 대검을 살 수 있어요" + (f" (남는 골드로 롱소드 {int((gold - p['bf']) // p['long'])}개)" if gold - p["bf"] >= p["long"] else "")
    n = int(gold // p["long"])
    return f"롱소드 {n}개를 살 수 있어요" if n else "아직 롱소드도 못 사요"
