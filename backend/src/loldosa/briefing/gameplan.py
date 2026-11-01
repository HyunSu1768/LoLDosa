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


LANE_NAME = {"top": "탑", "mid": "미드", "bot": "봇"}
OBJ_KO = {"dragon": "드래곤", "grub": "유충"}


def _first(text: str) -> str:
    """첫 문장만 (헤드라인용)."""
    head = text.split(". ")[0].rstrip(".")
    return head + "."


def _ss(sec) -> str:
    sec = max(0, int(sec or 0))
    return f"{sec // 60}:{sec % 60:02d}"


def build_game_plan(allies: list[int], enemies: list[int], ally_pos: dict[int, str], facts: dict,
                    name, timing_eid: str, trait_eid: str, ctx: dict | None = None) -> dict | None:
    """이 판에만 해당하는 사실로만 시간대별 할 일을 만든다. 어느 판에나 나올 일반론은 넣지 않는다.

    ctx (엔진이 통계에서 채움):
      lanes:  {"top"|"mid"|"bot": {"ally", "enemy", "gd", "n", "eid"}} — 이 라인 매치업의 10분 골드 차(표본으로 줄인 값)
      ejg:    {"name", "gank_lane", "gank_share", "gank_s", "n", "invade", "invade_base", "fd", "fd_base", "fg", "fg_base", "eid"}
      late:   {"ally": [(이름, %p)...], "enemy": [...], "eid"}
    각 줄은 챔피언 이름이나 이 판의 숫자가 들어가야만 만들어진다. 쓸 사실이 없는 시간대는 통째로 뺀다."""
    from .engine import josa

    ctx = ctx or {}
    us, them = team_profile(allies, name), team_profile(enemies, name)
    if not us:
        return None
    lanes, ejg, late = ctx.get("lanes", {}), ctx.get("ejg"), ctx.get("late")
    phases: list[Phase] = []

    def edge(lane, lo=150):
        x = lanes.get(lane)
        return x if x and abs(x["gd"]) >= lo else None

    # ---------- ~5분: 상대 정글 습관 + 라인 매치업으로 첫 갱·카정 방향 ----------
    p = Phase("early", "~5분", "초반", "")
    win = sorted([l for l in ("top", "mid", "bot") if edge(l) and lanes[l]["gd"] > 0], key=lambda l: -lanes[l]["gd"])
    lose = sorted([l for l in ("top", "mid", "bot") if edge(l) and lanes[l]["gd"] < 0], key=lambda l: lanes[l]["gd"])
    if ejg and ejg.get("gank_lane") and ejg["gank_share"] >= 0.42:
        gl = ejg["gank_lane"]
        mine = lanes.get(gl)
        who = f" 우리 {mine['ally']}" if mine else ""
        p.add(f"{josa(ejg['name'], '은는')} 첫 갱을 {josa(LANE_NAME[gl], '으로')} {round(ejg['gank_share'] * 100)}% 와요 (보통 {_ss(ejg['gank_s'])}, {ejg['n']}판). "
              f"{_ss(ejg['gank_s'] - 30)}쯤{who}에게 핑 찍고, 그 시간엔 반대편에서 바위게·카정을 챙겨요.", "fact", ejg["eid"])
    for l in win[:1]:
        x = lanes[l]
        p.add(f"{LANE_NAME[l]} {x['ally']} vs {x['enemy']}: 10분 골드 차 예상 {x['gd']:+,.0f}, 이기는 라인이에요 ({x['n']}판). 첫 갱은 {LANE_NAME[l]}에 쓰면 굴러가요.",
              "fact", x["eid"])
    for l in lose[:1]:
        x = lanes[l]
        p.add(f"{LANE_NAME[l]} {x['ally']} vs {x['enemy']}: 10분 골드 차 예상 {x['gd']:+,.0f}, 밀리는 라인이에요 ({x['n']}판). "
              f"상대 정글이 노리기 쉬워서 {LANE_NAME[l]} 쪽 역갱 위치를 잡아 두세요.", "fact", x["eid"])
    if ejg and ejg.get("invade") and ejg["invade"] >= ejg["invade_base"] * 1.35:
        p.add(f"{josa(ejg['name'], '은는')} 카정이 잦아요 (상대 정글 몹 평균 {ejg['invade']:.0f}개, 정글 평균 {ejg['invade_base']:.0f}개). "
              f"2:30쯤 내 정글 입구에 와드를 박아요.", "fact", ejg["eid"])
    # 3:00 상대 정글 위치는 '이번 판 플랜 · 주의'에 이미 있어서 여기선 반복하지 않는다
    if p.items:
        p.headline = _first(p.items[0]["text"])
        phases.append(p)

    # ---------- 5~15분: 어느 쪽 오브젝트를 이 판 라인 결과로 고르기 ----------
    p = Phase("objectives", "5~15분", "드래곤·유충", "")
    top_s = (lanes.get("top", {}).get("gd", 0)) + 0.5 * lanes.get("mid", {}).get("gd", 0)
    bot_s = (lanes.get("bot", {}).get("gd", 0)) + 0.5 * lanes.get("mid", {}).get("gd", 0)
    if abs(top_s - bot_s) >= 200 and (lanes.get("top") or lanes.get("bot")):
        pick, other = ("grub", "dragon") if top_s > bot_s else ("dragon", "grub")
        lane = "top" if pick == "grub" else "bot"
        x = lanes.get(lane)
        why = f"{LANE_NAME[lane]} {x['ally']}({x['gd']:+,.0f})" if x else LANE_NAME[lane]
        when = "8:00 유충" if pick == "grub" else "5:00 첫 드래곤"
        p.add(f"{why} 쪽이 이겨서 {when}을 노려요. {OBJ_KO[other]}은 상대가 가져가면 그 시간에 반대편 이득을 챙겨요.", "fact",
              *[lanes[l]["eid"] for l in ("top", "mid", "bot") if l in lanes])
    if ejg and ejg.get("fd") is not None and ejg.get("fd_base") and ejg["fd"] - ejg["fd_base"] >= 0.08:
        p.add(f"{josa(ejg['name'], '은는')} 첫 드래곤을 {round(ejg['fd'] * 100)}% 가져가요 (정글 평균 {round(ejg['fd_base'] * 100)}%). "
              f"4:30 전에 봇 강가 시야를 먼저 잡아요.", "fact", ejg["eid"])
    if ejg and ejg.get("fg") is not None and ejg.get("fg_base") and ejg["fg"] - ejg["fg_base"] >= 0.08:
        p.add(f"{josa(ejg['name'], '은는')} 첫 유충을 {round(ejg['fg'] * 100)}% 가져가요 (정글 평균 {round(ejg['fg_base'] * 100)}%). "
              f"7:30 전에 탑 강가 시야를 먼저 잡아요.", "fact", ejg["eid"])
    if p.items:
        p.headline = _first(p.items[0]["text"])
        p.add("드래곤은 5:00부터 5분마다, 공허 유충은 8:00에 3마리가 한 번만 나오고 14:45에 사라져요.", "rule", timing_eid)
        phases.append(p)

    # ---------- 15~20분: 조합의 핵심 챔피언 이름으로 ----------
    p = Phase("mid", "15~20분", "전령·사이드", "")
    t_us, t_them = us["type"], (them or {}).get("type")
    names_us = "·".join(us["core"][:3])
    if t_us == "split" and us.get("splitter"):
        sp = name(us["splitter"])
        p.add(f"{josa(sp, '이가')} 혼자 사이드를 밀 때 나머지는 반대편 오브젝트 근처에 있어요. 상대가 사이드로 2명 가면 그때 전령·드래곤을 쳐요.", "inference", trait_eid)
    elif t_us == "engage" and names_us:
        p.add(f"{josa(names_us, '이가')} 묶을 수 있을 때 다섯이 같이 싸워요. 좁은 정글 길목이나 오브젝트 앞이 좋아요.", "inference", trait_eid)
    elif t_us == "poke" and names_us:
        p.add(f"{names_us}로 오브젝트 앞에서 먼저 깎고 들어가요. 전령은 19:45 전에 미드 포탑에 써요.", "inference", trait_eid)
    elif t_us == "pick" and names_us:
        p.add(f"{josa(names_us, '이가')} 한 명을 끊으면 바로 오브젝트로 가요. 상대 정글 입구에 시야를 깔아요.", "inference", trait_eid)
    elif t_us == "protect" and names_us:
        p.add(f"{josa(names_us, '이가')} 지켜 주는 캐리 옆에서 싸우고, 먼저 들어가지 말아요.", "inference", trait_eid)
    if them and t_them in VS_NAMED and them["core"]:
        p.add(VS_NAMED[t_them].format(who=josa("·".join(them["core"][:3]), "이가"), who_plain="·".join(them["core"][:3])), "inference", trait_eid)
    mid = edge("mid")
    if mid:
        x = lanes["mid"]
        p.add(f"미드 {x['ally']} vs {x['enemy']} 10분 골드 차 예상 {x['gd']:+,.0f}: "
              + ("미드가 먼저 움직일 수 있어서 전령(15:00) 싸움에 유리해요." if x["gd"] > 0 else "미드가 늦게 움직여요. 전령은 미드가 밀어 둔 다음에 가요."),
              "fact", x["eid"])
    if p.items:
        p.headline = _first(p.items[0]["text"])
        p.add("전령은 15:00에 나와 19:45까지 있어요. 포탑 방패는 안 떨어지고 2·3차 포탑에도 있어요.", "rule", timing_eid)
        phases.append(p)

    # ---------- 20분~: 어느 챔피언이 후반에 강한지 이름과 숫자로 ----------
    p = Phase("late", "20분~", "바론·마무리", "")
    if late and (late.get("ally") or late.get("enemy")):
        a = "·".join(n for n, _ in late.get("ally", [])[:2])
        e = "·".join(n for n, _ in late.get("enemy", [])[:2])
        sa, se = late.get("ally_sum", 0.0), late.get("enemy_sum", 0.0)
        if se - sa >= 0.03 and e:
            p.add(f"상대 {josa(e, '은는')} 35분이 넘으면 승률이 오르는 챔피언이에요 (팀 평균 {se * 100:+.1f}%p, 우리 {sa * 100:+.1f}%p). "
                  f"20분 바론과 25분 전후 마무리를 노려요.", "fact", late["eid"])
        elif sa - se >= 0.03 and a:
            p.add(f"우리 {josa(a, '은는')} 35분이 넘으면 승률이 오르는 챔피언이에요 (팀 평균 {sa * 100:+.1f}%p, 상대 {se * 100:+.1f}%p). "
                  f"바론을 서두르지 말고 영혼·장로 싸움에서 이겨요.", "fact", late["eid"])
    if p.items:
        p.headline = _first(p.items[0]["text"])
        p.add("바론은 20:00에 나와요. 장로 드래곤은 한 팀이 영혼을 얻고 6분 뒤에 나와요.", "rule", timing_eid)
        phases.append(p)

    return {
        "us": {"type": t_us, "label": TYPE_KO[t_us], "why": _why(us)},
        "them": ({"type": t_them, "label": TYPE_KO[t_them], "why": _why(them)} if them else None),
        "vs": None,
        "phases": [asdict(x) for x in phases],
    }


# 상대 조합 대처 (상대 핵심 챔피언 이름을 넣어서)
VS_NAMED = {
    "engage": "상대는 {who} 들어오는 조합이에요. 좁은 길목에서 먼저 싸우지 말고, 오브젝트 앞에선 진입 길에 시야부터 봐 두세요.",
    "poke": "상대 {who_plain}에게 오래 대치하면 깎이기만 해요. 시야를 먼저 잡고 짧게 들어가거나 옆으로 돌아 들어가요.",
    "pick": "상대 {who} 끊는 조합이에요. 시야 없는 정글엔 혼자 들어가지 말고, 와드는 둘이 같이 박아요.",
    "protect": "상대 {who} 캐리를 지켜 줘요. 뒤 캐리를 바로 노리기 어려우니 사이드와 오브젝트 교환으로 시간을 써요.",
    "split": "상대 {who} 혼자 사이드를 밀어요. 그 라인은 1명이 받고, 나머지는 반대편 오브젝트를 4:4로 노려요.",
}
