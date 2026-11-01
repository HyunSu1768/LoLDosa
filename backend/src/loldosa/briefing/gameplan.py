"""게임 전 '전체 운영 플랜': 양 팀 조합 + 2026 오브젝트 시간표 → 초반·중반·후반에 할 일.

근거 두 층:
1) 2026 오브젝트 시간 (드래곤 5:00 · 유충 8:00~14:45 · 전령 15:00~19:45 · 바론 20:00 · 포탑 방패 안 떨어짐 · 아타칸 없음)
   - KR 솔랭 4,616판(패치 26.19~26.21) 실제 처치 시각으로 확인 (research_notes/2026 롤 운영 게임 플랜/data_check.md)
2) 조합 유형: 챔피언마다 실제 경기에서 한 일(묶기·포킹·같이 끊기·회복/보호막·혼자 민 포탑·건물 피해)을
   챔피언끼리 비교한 백분위 (scripts/build_champ_traits.py → learn/champ_traits.json).
   유형별 운영 방법은 코칭 자료를 정리한 것이라 '판단(inference)'으로 표시한다 (reports/2026 롤 운영 게임 플랜.md).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path

TRAITS_PATH = Path(__file__).resolve().parents[1] / "learn" / "champ_traits.json"
TYPES = ("engage", "poke", "pick", "protect", "split")
TYPE_KO = {"engage": "한타·돌진 조합", "poke": "포킹·공성 조합", "pick": "끊기(픽) 조합", "protect": "지키기(보호) 조합",
           "split": "사이드(스플릿) 조합", "balanced": "고른 조합"}
TYPE_WHY = {"engage": "상대를 묶고 맞아 주는 챔피언이 많아요", "poke": "멀리서 피해를 주고 덜 맞는 챔피언이 많아요",
            "pick": "같이 끊는 킬이 많은 챔피언이 많아요", "protect": "아군을 회복·보호하는 챔피언이 많아요",
            "split": "혼자 포탑을 미는 챔피언이 있어요", "balanced": "한쪽으로 치우친 성향이 없어요"}


@dataclass
class Phase:
    key: str
    time: str
    title: str
    headline: str
    items: list[dict] = field(default_factory=list)  # {text, kind: rule|inference, evidence}

    def add(self, text: str, kind: str = "inference", *ev: str) -> None:
        self.items.append({"text": text, "kind": kind, "evidence": [e for e in ev if e]})


@lru_cache(maxsize=1)
def traits() -> dict:
    if not TRAITS_PATH.exists():
        return {}
    return json.loads(TRAITS_PATH.read_text(encoding="utf-8"))


CORE = {"engage": 0.7, "poke": 0.75, "pick": 0.8, "protect": 0.85, "split": 0.8}  # 이 이상이면 그 유형의 '핵심 챔피언'
# 겹칠 때 우선순위: 돌진 챔피언은 대개 끊기 점수도 높고(서포터 CC), 회복 서포터 한 명만으로는 조합 성격이 약해서 살짝 낮춘다
TIE = {"engage": 1.0, "poke": 1.0, "pick": 0.9, "protect": 0.8, "split": 1.0}
NEED = {"engage": 2, "poke": 2, "pick": 2, "protect": 1, "split": 1}  # 유형으로 보려면 핵심 챔피언이 몇 명 필요한지


def team_profile(ids: list[int], name=lambda c: str(c)) -> dict | None:
    """팀 유형: 유형마다 '핵심 챔피언'(챔피언끼리 비교해 상위권)이 몇 명인지 센다.

    다섯 명 평균을 쓰면 성향이 뭉개져요(예: 말파이트·노틸러스가 있어도 카이사·오리아나 때문에 돌진 점수가 평균이 됨).
    조합은 핵심 챔피언 몇 명이 정하는 거라서, 기준을 넘는 챔피언 수로 판단해요. 성향을 아는 챔피언이 3명 미만이면 None."""
    tr = traits().get("champions", {})
    known = [c for c in ids if str(c) in tr]
    if len(known) < 3:
        return None
    core = {k: [c for c in known if tr[str(c)][k] >= CORE[k] and (k != "protect" or tr[str(c)].get("support"))] for k in TYPES}
    # 필요한 수를 채운 유형 중 핵심 챔피언 점수 합이 가장 큰 것
    ok = {k: sum(tr[str(c)][k] for c in v) / NEED[k] * TIE[k] for k, v in core.items() if len(v) >= NEED[k]}
    kind = max(ok, key=ok.get) if ok else "balanced"
    avg = {k: sum(tr[str(c)][k] for c in known) / len(known) for k in ("late", "tank")}
    return {"type": kind, "core": [name(c) for c in core.get(kind, [])] if kind != "balanced" else [],
            "counts": {k: len(v) for k, v in core.items()}, "late": round(avg["late"], 3), "tank": round(avg["tank"], 3),
            "splitter": core["split"][0] if core["split"] else None, "n": len(known)}


def _why(p: dict) -> str:
    from .engine import josa

    if p["type"] == "balanced" or not p["core"]:
        return TYPE_WHY["balanced"]
    who = "·".join(p["core"][:3])
    return {"engage": f"{josa(who, '이가')} 상대를 잘 묶고 앞에서 맞아 줘요",
            "poke": f"{josa(who, '이가')} 멀리서 피해를 주고 덜 맞아요",
            "pick": f"{josa(who, '이가')} 같이 끊는 킬이 많아요",
            "protect": f"{josa(who, '이가')} 아군을 회복·보호해요",
            "split": f"{josa(who, '이가')} 혼자 포탑을 잘 밀어요"}[p["type"]]


# 상대 유형별 대처 (코칭 자료 정리: 포킹 < 돌진 < 받아치기, 돌진은 사이드·공성에 약함)
VS = {
    "engage": "상대가 한타·돌진 조합이에요. 좁은 길목에서 먼저 싸우지 말고, 넓은 곳에서 받아쳐요. 오브젝트 앞에선 먼저 시야를 잡아 진입 길을 봐 두세요.",
    "poke": "상대가 포킹 조합이에요. 오브젝트 앞에서 오래 대치하면 깎이기만 해요. 시야를 먼저 잡고 짧게 들어가거나, 정글 쪽으로 돌아 들어가요.",
    "pick": "상대가 끊기 조합이에요. 시야 없는 정글에 혼자 들어가지 말고, 와드는 둘이 같이 박아요.",
    "protect": "상대가 지키기 조합이에요. 뒤에 있는 캐리를 바로 노리기 어려워요. 앞라인부터 정면으로 싸우기보다 사이드와 오브젝트 교환으로 시간을 써요.",
    "split": "상대에 혼자 사이드를 미는 챔피언이 있어요. 그 라인은 1명이 받고, 나머지는 반대편 오브젝트를 4:4로 노려요.",
}


def build_game_plan(allies: list[int], enemies: list[int], ally_pos: dict[int, str], facts: dict,
                    name, timing_eid: str, trait_eid: str) -> dict | None:
    """allies/enemies: 챔피언 id, ally_pos: id → 'top'/'jungle'/'middle'/'bottom'/'utility', name: id → 이름."""
    us, them = team_profile(allies, name), team_profile(enemies, name)
    if not us:
        return None
    # 후반 힘: 엔진의 실제 시간대별 승률(scaling) 사실이 있으면 우선, 없으면 성향 점수 차이
    sc = facts.get("scaling")
    if sc:
        late_who, late_eid = sc["who"], sc["eid"]
    elif them and abs(us["late"] - them["late"]) >= 0.06:
        late_who, late_eid = ("ally" if us["late"] > them["late"] else "enemy"), trait_eid
    else:
        late_who, late_eid = None, None
    side = (facts.get("obj_side") or {}).get("side")  # 'dragon'(봇이 유리) / 'grub'(탑이 유리)
    side_eids = (facts.get("obj_side") or {}).get("eids", [])
    t_us, t_them = us["type"], (them or {}).get("type")

    phases: list[Phase] = []

    # 1) 0:00~5:00
    p = Phase("early", "~5분", "초반", "")
    p.add("캠프는 0:55(두꺼비·돌거북 1:07), 바위게는 2:55에 나와요. 풀캠이면 바위게 시간과 맞아요.", "rule", timing_eid)
    if late_who == "enemy":
        p.headline = "상대가 후반 조합이라 초반에 차이를 벌려야 해요"
        p.add("2·3레벨에 싸움과 카정을 노려요. 첫 킬 100골드, 첫 포탑 300골드가 다시 생겼어요.", "inference", late_eid)
    elif late_who == "ally":
        p.headline = "우리가 후반 조합이라 첫 귀환 전 싸움은 피해요"
        p.add("풀캠으로 레벨을 챙기고, 상대 정글 반대쪽에서 움직여요. 손해만 안 보면 시간이 우리 편이에요.", "inference", late_eid)
    else:
        p.headline = "풀캠을 마치고 바위게에서 첫 싸움 여부를 정해요"
        p.add("라인 주도권이 있는 쪽 바위게만 싸워요. 주도권이 없으면 반대쪽 바위게나 캠프를 먹어요.", "inference")
    phases.append(p)

    # 2) 5:00~14:45 드래곤·유충
    p = Phase("objectives", "5~15분", "드래곤·유충", "")
    p.add("드래곤은 5:00부터 5분마다, 공허 유충은 8:00에 3마리가 한 번만 나오고 14:45에 사라져요.", "rule", timing_eid)
    prefer = None
    if side == "dragon":
        prefer, why, ev = "dragon", "봇 라인전이 유리해서", side_eids
    elif side == "grub":
        prefer, why, ev = "grub", "탑 라인전이 유리해서", side_eids
    elif t_us in ("poke", "split"):
        prefer, why, ev = "grub", "포탑을 미는 조합이라 (유충은 건물 피해를 올려요)", [trait_eid]
    elif t_us == "protect" or late_who == "ally":
        prefer, why, ev = "dragon", "후반 조합이라 드래곤 영혼을 보고", [late_eid or trait_eid]
    if prefer == "dragon":
        p.headline = "드래곤 쪽에 힘을 줘요"
        p.add(f"{why} 드래곤을 먼저 챙겨요. 유충은 상대가 가져가면 그 시간에 드래곤을 맞교환해요.", "inference", *ev)
    elif prefer == "grub":
        p.headline = "8:00 유충 쪽에 힘을 줘요"
        p.add(f"{why} 유충 3마리를 노려요. 첫 드래곤은 상대가 가져가면 반대편에서 이득을 챙겨요.", "inference", *ev)
    else:
        p.headline = "주도권이 있는 쪽 오브젝트로 가요"
        p.add("라인 주도권이 있는 쪽 오브젝트만 싸우고, 없는 쪽은 맞교환해요.", "inference")
    p.add("오브젝트 90초 전에 귀환하고, 60초 전 제어 와드, 30초 전 입구 와드를 박아요.", "inference")
    phases.append(p)

    # 3) 15:00~20:00 전령·사이드
    p = Phase("mid", "15~20분", "전령·사이드", "")
    p.add("전령은 15:00에 나와 19:45까지 있어요. 포탑 방패는 이제 안 떨어지고 2·3차 포탑에도 생겼어요.", "rule", timing_eid)
    if t_us == "split" and us.get("splitter"):
        from .engine import josa

        sp = name(us["splitter"])
        p.headline = f"{sp} 사이드를 밀고, 나는 반대편을 봐요"
        p.add(f"{josa(sp, '이가')} 혼자 사이드를 밀 때 나머지는 반대편 오브젝트 근처에 있어요. 상대가 사이드로 2명 가면 그때 오브젝트를 쳐요.", "inference", trait_eid)
    elif t_us == "engage":
        p.headline = "다섯이 뭉쳐서 드래곤·전령 앞에서 싸움을 걸어요"
        p.add("싸움은 좁은 정글 길목이나 오브젝트 앞에서 걸어요. 넓은 곳에선 상대가 피해요.", "inference", trait_eid)
    elif t_us == "poke":
        p.headline = "전령으로 미드 포탑을 깨고 대치에서 깎아요"
        p.add("전령은 19:45 전에 꼭 포탑에 써요. 오브젝트 30~60초 전에 먼저 도착해 시야를 잡고 깎은 뒤 쳐요.", "inference", trait_eid)
    elif t_us == "pick":
        p.headline = "상대 정글에 시야를 깔고 한 명을 끊은 뒤 바로 오브젝트로 가요"
        p.add("끊은 직후가 오브젝트 타이밍이에요. 잡고 나서 귀환부터 하면 이득이 사라져요.", "inference", trait_eid)
    elif t_us == "protect":
        p.headline = "캐리 옆에 붙어서 버티고, 오브젝트는 맞교환해요"
        p.add("먼저 들어가지 말고 상대가 들어오면 받아쳐요. 캐리 아이템이 나오기 전 싸움은 줄여요.", "inference", trait_eid)
    else:
        p.headline = "전령을 포탑에 쓰고, 이긴 라인 쪽으로 사이드를 밀어요"
        p.add("전령은 19:45 전에 포탑에 써야 의미가 있어요.", "inference")
    phases.append(p)

    # 4) 20:00~ 바론·마무리
    p = Phase("late", "20분~", "바론·마무리", "")
    p.add("바론은 20:00에 나와요. 장로 드래곤은 한 팀이 영혼을 얻고 6분 뒤에 나와요.", "rule", timing_eid)
    if late_who == "enemy":
        p.headline = "20~25분 바론으로 끝내요. 늦어질수록 불리해요"
        p.add("한 명이라도 끊으면 바로 바론을 치고, 버프로 포탑을 깨요. 버프가 끝나면 무리하지 말고 귀환해요.", "inference", late_eid)
    elif late_who == "ally":
        p.headline = "서두르지 말고 영혼·장로·바론 싸움에서 이겨요"
        p.add("먼저 싸움을 걸 필요가 없어요. 시야를 잡고 상대가 들어오게 만들어요.", "inference", late_eid)
    else:
        p.headline = "인원이 많을 때만 바론을 쳐요"
        p.add("상대보다 사람이 많거나 상대 정글이 죽었을 때만 바론을 쳐요.", "inference")
    phases.append(p)

    return {
        "us": {"type": t_us, "label": TYPE_KO[t_us], "why": _why(us), "late": us["late"]},
        "them": ({"type": t_them, "label": TYPE_KO[t_them], "why": _why(them), "late": them["late"]} if them else None),
        "vs": VS.get(t_them) if t_them else None,
        "late_who": late_who,
        "phases": [asdict(x) for x in phases],
    }
