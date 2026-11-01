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
    items: list[dict] = field(default_factory=list)  # {text(할 일), why(왜), kind: fact|inference|rule, evidence}
    why: str = ""  # 헤드라인(첫 할 일)의 이유

    def add(self, text: str, kind: str = "inference", *ev: str, why: str = "") -> None:
        self.items.append({"text": text, "why": why, "kind": kind, "evidence": [e for e in ev if e]})


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
    top_pct = (round((1 - min(tr[str(c)][kind] for c in core[kind])) * 100) if kind in core and core[kind] else None)
    return {"type": kind, "core": [name(c) for c in core.get(kind, [])] if kind != "balanced" else [], "top_pct": top_pct,
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
    """이 판에만 해당하는 사실로 '할 일 + 왜'를 시간대별로 만든다. 어느 판에나 나올 일반론은 넣지 않는다.

    '왜'는 두 겹: (1) 이 판 데이터(상대 정글 동선·라인별 10분 골드·챔피언 성향 백분위)
                  (2) 그 데이터가 게임 안에서 무슨 뜻인지 (예: 풀캠이 끝나는 쪽 → 가장 가까운 라인에 첫 갱)
    ctx (엔진이 통계에서 채움):
      lanes: {"top"|"mid"|"bot": {"ally", "enemy", "gd", "ga", "ge", "n", "eid"}}
      ejg:   {"name", "gank_lane", "gank_share", "gank_s", "n", "invade", "invade_base", "fd", "fd_base", "fg", "fg_base",
              "route": {"start", "start_p", "side3", "side3_p", "clear", "clear_p"}, "eid", "route_eid"}
      late:  {"ally": [(이름, 차)], "enemy": [...], "ally_sum", "enemy_sum", "eid"}"""
    from .engine import josa

    ctx = ctx or {}
    us, them = team_profile(allies, name), team_profile(enemies, name)
    if not us:
        return None
    lanes, ejg, late = ctx.get("lanes", {}), ctx.get("ejg"), ctx.get("late")
    phases: list[Phase] = []
    SIDE = {"top": "탑", "bot": "봇"}
    CLEAR = {"full_clear": "풀캠", "partial": "4~5캠프", "three_or_less": "3캠프 이하"}

    def edge(lane, lo=150):
        x = lanes.get(lane)
        return x if x and abs(x["gd"]) >= lo else None

    def finish(p: Phase) -> None:
        if p.items:
            p.headline = _first(p.items[0]["text"])
            p.why = p.items[0]["why"]
            phases.append(p)

    # ---------- ~5분 ----------
    p = Phase("early", "~5분", "초반", "")
    if ejg and ejg.get("gank_lane") and ejg["gank_share"] >= 0.42:
        gl, en, rt = ejg["gank_lane"], ejg["name"], ejg.get("route")
        other = "탑" if gl == "bot" else "봇"
        mine = lanes.get(gl)
        who = f"{mine['ally']}에게 " if mine else ""
        if rt and rt.get("side3") == gl:
            why = (f"{josa(en, '은는')} {SIDE.get(rt['start'], '?')} 쪽에서 시작하는 판이 {rt['start_p']:.0%}이고, "
                   f"{josa(CLEAR.get(rt['clear'], '정글링'), '을를')} 마친 3:00엔 {SIDE[gl]} 쪽에 있는 판이 {rt['side3_p']:.0%}예요. "
                   f"정글링이 끝난 자리에서 가장 가까운 라인이 {SIDE[gl]}이라 첫 갱이 {josa(SIDE[gl], '으로')} 와요 "
                   f"({ejg['n']}판 중 {round(ejg['gank_share'] * 100)}%, 보통 {_ss(ejg['gank_s'])}). "
                   f"그동안 {other} 쪽 상대 정글은 비어 있어요.")
            ev = (ejg["eid"], ejg.get("route_eid"))
        else:
            why = (f"{josa(en, '은는')} 첫 갱을 {josa(SIDE.get(gl, gl), '으로')} 오는 판이 {round(ejg['gank_share'] * 100)}%예요 "
                   f"(보통 {_ss(ejg['gank_s'])}, {ejg['n']}판). 상대 정글이 {SIDE.get(gl, gl)}에 있는 동안 {other} 쪽은 비어 있어요.")
            ev = (ejg["eid"],)
        p.add(f"{_ss(ejg['gank_s'] - 30)}쯤 {who}{SIDE.get(gl, gl)} 핑을 찍고, 그 시간엔 {other} 쪽 바위게나 상대 캠프를 챙겨요.",
              "fact", *ev, why=why)
    win = sorted([l for l in ("top", "mid", "bot") if edge(l) and lanes[l]["gd"] > 0], key=lambda l: -lanes[l]["gd"])
    lose = sorted([l for l in ("top", "mid", "bot") if edge(l) and lanes[l]["gd"] < 0], key=lambda l: lanes[l]["gd"])
    for l in win[:1]:
        x = lanes[l]
        p.add(f"첫 갱은 {LANE_NAME[l]}에 써요 ({x['ally']} vs {x['enemy']}).", "fact", x["eid"],
              why=(f"{josa(x['ally'], '은는')} {LANE_NAME[l]}에서 10분까지 평균 {x['ga']:+,.0f}골드, {josa(x['enemy'], '은는')} {x['ge']:+,.0f}골드를 내서 "
                   f"우리가 {x['gd']:,.0f}골드쯤 앞서는 라인이에요. 밀리는 쪽 라이너는 체력·아이템이 부족해서 갱 한 번에 킬이나 귀환이 나기 쉬워요. "
                   f"킬이 나면 {LANE_NAME[l]}이 포탑 방패를 먼저 깨고, 이긴 라이너는 바위게·오브젝트에 먼저 와요."))
    for l in lose[:1]:
        x = lanes[l]
        p.add(f"{LANE_NAME[l]} 근처에서 역갱을 노려요 ({x['ally']} vs {x['enemy']}).", "fact", x["eid"],
              why=(f"{josa(x['enemy'], '은는')} {LANE_NAME[l]}에서 10분까지 평균 {x['ge']:+,.0f}골드, {josa(x['ally'], '은는')} {x['ga']:+,.0f}골드라 "
                   f"상대가 {abs(x['gd']):,.0f}골드쯤 앞서는 라인이에요. 앞서는 쪽은 라인을 밀고 앞으로 나와요. 앞으로 나온 라이너가 있는 곳엔 상대 정글도 갱을 오기 쉬워서, "
                   f"내가 근처에 있으면 2:2 싸움을 우리 쪽에서 받을 수 있어요."))
    if ejg and ejg.get("invade") and ejg["invade"] >= ejg["invade_base"] * 1.35:
        p.add("2:30쯤 내 정글 입구에 와드를 박아요.", "fact", ejg["eid"],
              why=(f"{josa(ejg['name'], '은는')} 상대 정글 몹을 한 판에 평균 {ejg['invade']:.0f}개 먹어요 (정글 평균 {ejg['invade_base']:.0f}개). "
                   f"카정을 자주 오는 챔피언이라 캠프를 뺏기면 레벨이 밀려요. 먼저 보면 캠프를 비우거나 라이너를 불러 같이 싸울 수 있어요."))
    finish(p)

    # ---------- 5~15분 ----------
    p = Phase("objectives", "5~15분", "드래곤·유충", "")
    top_s = lanes.get("top", {}).get("gd", 0) + 0.5 * lanes.get("mid", {}).get("gd", 0)
    bot_s = lanes.get("bot", {}).get("gd", 0) + 0.5 * lanes.get("mid", {}).get("gd", 0)
    if abs(top_s - bot_s) >= 200 and (lanes.get("top") or lanes.get("bot")):
        pick = "grub" if top_s > bot_s else "dragon"
        lane, where = ("top", "탑 쪽 강") if pick == "grub" else ("bot", "봇 쪽 강")
        x = lanes.get(lane)
        when = "8:00 유충" if pick == "grub" else "5:00 첫 드래곤"
        trade = "드래곤" if pick == "grub" else "유충"
        winners = f"{LANE_NAME[lane]} {x['ally']}" if x else LANE_NAME[lane]
        p.add(f"{josa(when, '을를')} 노리고, {josa(trade, '은는')} 내줘도 돼요.", "fact", *[lanes[l]["eid"] for l in ("top", "mid", "bot") if l in lanes],
              why=(f"{'유충' if pick == 'grub' else '드래곤'}은 {where}에 있어요. 오브젝트 싸움엔 근처 라이너가 먼저 와야 이기는데, "
                   f"라인을 이긴 라이너는 라인을 밀어 놓고 먼저 움직일 수 있어요. 이 판은 {winners} 쪽이 이기는 라인이라 그쪽이 먼저 와요. "
                   f"반대편 {josa(trade, '은는')} 상대가 가져가는 시간에 우리가 {'유충' if pick == 'grub' else '드래곤'}·포탑으로 바꾸면 손해가 아니에요."))
    rt = (ejg or {}).get("route") or {}
    chosen = "grub" if (abs(top_s - bot_s) >= 200 and top_s > bot_s) else "dragon" if abs(top_s - bot_s) >= 200 else None
    # 내주기로 한 쪽 오브젝트의 시야 줄은 빼서 앞뒤가 안 맞는 말을 하지 않는다
    if chosen != "grub" and ejg and ejg.get("fd") is not None and ejg.get("fd_base") and ejg["fd"] - ejg["fd_base"] >= 0.08:
        extra = (f" 이 챔피언은 3:00에 봇 쪽에 있는 판이 {rt['side3_p']:.0%}라 5:00 드래곤과 동선이 이어져요." if rt.get("side3") == "bot" else "")
        p.add("4:30 전에 봇 강가 시야를 먼저 잡아요.", "fact", ejg["eid"],
              why=f"{josa(ejg['name'], '은는')} 첫 드래곤을 {round(ejg['fd'] * 100)}% 가져가요 (정글 평균 {round(ejg['fd_base'] * 100)}%).{extra} "
                  f"드래곤 앞 시야를 먼저 잡은 쪽이 상대가 오는 걸 보고 싸울지 정할 수 있어요.")
    if chosen != "dragon" and ejg and ejg.get("fg") is not None and ejg.get("fg_base") and ejg["fg"] - ejg["fg_base"] >= 0.08:
        extra = (f" 이 챔피언은 3:00에 탑 쪽에 있는 판이 {rt['side3_p']:.0%}예요." if rt.get("side3") == "top" else "")
        p.add("7:30 전에 탑 강가 시야를 먼저 잡아요.", "fact", ejg["eid"],
              why=f"{josa(ejg['name'], '은는')} 첫 유충을 {round(ejg['fg'] * 100)}% 가져가요 (정글 평균 {round(ejg['fg_base'] * 100)}%).{extra} "
                  f"유충 앞 시야를 먼저 잡은 쪽이 싸울지 정할 수 있어요.")
    if p.items:
        p.add("드래곤은 5:00부터 5분마다, 공허 유충은 8:00에 3마리가 한 번만 나오고 14:45에 사라져요.", "rule", timing_eid)
    finish(p)

    # ---------- 15~20분 ----------
    p = Phase("mid", "15~20분", "전령·사이드", "")
    t_us, t_them = us["type"], (them or {}).get("type")
    nm = "·".join(us["core"][:3])
    pct = f"상위 {us['top_pct']}%" if us.get("top_pct") is not None else "상위권"
    if t_us == "split" and us.get("splitter"):
        sp = name(us["splitter"])
        p.add(f"{josa(sp, '이가')} 사이드를 밀 때 나머지는 반대편 오브젝트 근처에 있어요.", "inference", trait_eid,
              why=(f"{josa(sp, '은는')} 후반에 혼자 포탑을 민 기록이 챔피언 중 {pct}예요. 상대는 막으러 1~2명을 보내야 하고, "
                   f"그만큼 반대편은 우리가 사람 수에서 앞서요. 그때 전령·드래곤을 쳐요."))
    elif t_us == "engage" and nm:
        p.add("좁은 정글 길목이나 오브젝트 앞에서 다섯이 같이 싸워요.", "inference", trait_eid,
              why=(f"{josa(nm, '은는')} 상대를 묶은 횟수·시간과 맞아 준 비중이 챔피언 중 {pct}예요. "
                   f"좁은 곳에서 한 번 묶이면 상대 여러 명이 같이 맞고, 넓은 곳에선 상대가 흩어져서 피해요."))
    elif t_us == "poke" and nm:
        p.add("오브젝트 앞에 먼저 가서 깎은 다음에 들어가요. 전령은 19:45 전에 미드 포탑에 써요.", "inference", trait_eid,
              why=(f"{josa(nm, '은는')} 받은 피해에 비해 주는 피해가 큰 챔피언이에요 (챔피언 중 {pct}). "
                   f"대치가 길어질수록 상대 체력만 줄어서, 깎인 상대는 오브젝트를 지키지 못하고 물러나요."))
    elif t_us == "pick" and nm:
        p.add("상대 정글 입구에 시야를 깔고, 한 명을 끊으면 바로 오브젝트로 가요.", "inference", trait_eid,
              why=(f"{josa(nm, '은는')} 같이 끊는 킬이 챔피언 중 {pct}예요. 한 명이 빠진 4:5에선 상대가 오브젝트를 지킬 수 없어요. "
                   f"끊고 나서 귀환부터 하면 그 시간이 지나가요."))
    elif t_us == "protect" and nm:
        p.add("캐리 옆에서 싸우고 먼저 들어가지 않아요.", "inference", trait_eid,
              why=(f"{josa(nm, '은는')} 아군 회복·보호막이 챔피언 중 {pct}예요. 캐리가 오래 살아남는 게 이 조합의 힘이라, "
                   f"먼저 들어가서 흩어지면 그 장점이 사라져요."))
    if them and t_them in VS_NAMED and them["core"]:
        act, why = VS_NAMED[t_them]
        who = "·".join(them["core"][:3])
        tp = f"상위 {them['top_pct']}%" if them.get("top_pct") is not None else "상위권"
        p.add(act.format(who=who), "inference", trait_eid, why=why.format(who=josa(who, "은는"), pct=tp))
    mid = edge("mid")
    if mid:
        x = lanes["mid"]
        up = x["gd"] > 0
        p.add("전령(15:00)은 미드가 밀어 둔 다음에 같이 가요." if not up else "전령(15:00) 싸움은 미드와 같이 먼저 자리 잡아요.", "fact", x["eid"],
              why=(f"미드 {josa(x['ally'], '은는')} 10분까지 평균 {x['ga']:+,.0f}골드, {josa(x['enemy'], '은는')} {x['ge']:+,.0f}골드를 내요. "
                   f"미드는 양쪽 강에 가장 빨리 가는 라인이라, "
                   + ("라인을 이기는 우리 미드가 먼저 움직일 수 있어요." if up else "라인이 밀리면 우리 미드가 늦게 와요.")))
    if p.items:
        p.add("전령은 15:00에 나와 19:45까지 있어요. 포탑 방패는 안 떨어지고 2·3차 포탑에도 있어요.", "rule", timing_eid)
    finish(p)

    # ---------- 20분~ ----------
    p = Phase("late", "20분~", "바론·마무리", "")
    if late and (late.get("ally") or late.get("enemy")):
        a = "·".join(n for n, _ in late.get("ally", [])[:2])
        e = "·".join(n for n, _ in late.get("enemy", [])[:2])
        sa, se = late.get("ally_sum", 0.0), late.get("enemy_sum", 0.0)
        if se - sa >= 0.03 and e:
            p.add("20분 바론과 25분 전후 마무리를 노려요.", "fact", late["eid"],
                  why=(f"상대 {josa(e, '은는')} 30분이 넘은 판에서 승률이 오르는 챔피언이에요 (팀 평균 {se * 100:+.1f}%p, 우리 {sa * 100:+.1f}%p). "
                       f"아이템이 쌓일수록 강해진다는 뜻이라, 시간이 갈수록 상대가 유리해져요."))
        elif sa - se >= 0.03 and a:
            p.add("바론을 서두르지 말고 영혼·장로 싸움에서 이겨요.", "fact", late["eid"],
                  why=(f"우리 {josa(a, '은는')} 30분이 넘은 판에서 승률이 오르는 챔피언이에요 (팀 평균 {sa * 100:+.1f}%p, 상대 {se * 100:+.1f}%p). "
                       f"아이템이 쌓일수록 강해진다는 뜻이라, 무리한 싸움만 안 하면 시간이 우리 편이에요."))
    if p.items:
        p.add("바론은 20:00에 나와요. 장로 드래곤은 한 팀이 영혼을 얻고 6분 뒤에 나와요.", "rule", timing_eid)
    finish(p)

    return {
        "us": {"type": t_us, "label": TYPE_KO[t_us], "why": _why(us)},
        "them": ({"type": t_them, "label": TYPE_KO[t_them], "why": _why(them)} if them else None),
        "vs": None,
        "phases": [asdict(x) for x in phases],
    }


# 상대 조합 대처 (상대 핵심 챔피언 이름을 넣어서)
VS_NAMED = {  # (할 일, 왜)
    "engage": ("좁은 길목에서 먼저 싸우지 말고, 오브젝트 앞에선 상대 진입 길에 시야부터 봐 둬요.",
               "상대 {who} 상대를 묶는 기록이 챔피언 중 {pct}예요. 좁은 곳에서 묶이면 여럿이 같이 맞아서, 넓은 곳에서 받아치는 게 유리해요."),
    "poke": ("오브젝트 앞에서 오래 대치하지 말고, 시야를 먼저 잡고 짧게 들어가요.",
             "상대 {who} 받은 피해보다 주는 피해가 큰 챔피언이에요 (챔피언 중 {pct}). 대치가 길어질수록 우리 체력만 줄어요."),
    "pick": ("시야 없는 정글엔 혼자 들어가지 말고, 와드는 둘이 같이 박아요.",
             "상대 {who} 같이 끊는 킬이 챔피언 중 {pct}예요. 혼자 있는 한 명이 잡히면 4:5가 돼서 오브젝트를 못 지켜요."),
    "protect": ("뒤 캐리를 바로 노리지 말고, 사이드와 오브젝트 교환으로 시간을 써요.",
                "상대 {who} 아군 회복·보호막이 챔피언 중 {pct}예요. 정면 싸움에선 캐리가 오래 살아서 우리가 먼저 지쳐요."),
    "split": ("사이드는 1명이 받고, 나머지는 반대편 오브젝트를 4:4로 노려요.",
              "상대 {who} 후반에 혼자 포탑을 민 기록이 챔피언 중 {pct}예요. 둘이 막으러 가면 반대편에서 사람이 모자라요."),
}


# ---------------------------------------------------------------- 한타
# 근거: KR 솔랭 4,616판 타임라인에서 찾은 한타 35,480개 (scripts/fight_stats.py, research_notes/2026 롤 한타 운영/data_fights.md)
# 주의: '첫 킬 팀이 한타 73.7% 승'은 3킬 이상·동률 제외 정의에서 동전 던지기로도 73.8%가 나오는 산수 효과라 쓰지 않는다
#       (scripts/fight_null.py). 대신 정의에 안 묶이는 오브젝트 결과를 쓴다 (scripts/fight_objective.py).
FK_DRAGON, FK_BARON = 0.619, 0.684  # 오브젝트 근처 한타 첫 킬 팀이 그 오브젝트를 가져간 비율 (기준 50%)
JG_DEAD_DRAGON, JG_DEAD_BARON = 0.703, 0.80  # 정글이 그 한타 첫 데스면 상대가 가져간 비율 (강타가 같이 사라짐)
SECOND_OTHER = 0.528  # 첫 킬 직후 두 번째 킬을 상대 팀이 낸 비율: 끊고 쫓으면 받아치기를 당한다
DRAGON_AFTER_FIGHT, BARON_AFTER_FIGHT = 0.784, 0.875  # 근처 한타를 이긴 팀이 그 오브젝트를 가져간 비율
FRONT, CARRY = 0.231, 0.236  # 받은 피해 비중 상위 25% = 앞라인, 팀 딜 비중 상위 25% = 핵심 딜러


def _pct_top(v: float) -> int:
    return max(1, round((1 - v) * 100))


def build_fight_plan(me: int, allies: list[int], enemies: list[int], name, tags, fight_eid: str, trait_eid: str) -> list[dict]:
    """이 판 10명으로 한타에서 할 일 + 왜. tags: id → Data Dragon 태그 튜플.

    역할은 내 챔피언이 실제 경기에서 한 일(묶기·받은 피해·팀 딜 비중)로 정하고, 노릴 대상·지킬 대상은 양 팀의 팀 딜 비중으로 고른다.
    '왜'에는 이 판 챔피언 수치와, 우리 데이터의 한타 통계(첫 킬 팀 73.7% 승 등)를 같이 쓴다."""
    from .engine import josa

    tr = traits().get("champions", {})
    T = lambda c: tr.get(str(c))  # noqa: E731
    out: list[dict] = []

    def add(text, why, kind="inference", *ev):
        out.append({"text": text, "why": why, "kind": kind, "evidence": [e for e in ev if e]})

    def carry_of(ids, skip=()):
        rows = [(T(c)["dmg_share"], c) for c in ids if T(c) and c not in skip]
        return max(rows) if rows else None

    mt = T(me)
    if not mt:
        return out
    mn = name(me)
    e_carry = carry_of(enemies)
    a_carry = carry_of(allies, skip=(me,))
    e_cc = [c for c in enemies if T(c) and T(c)["engage"] >= 0.7]
    # 뒤로 파고드는 챔피언: 대표 태그(첫 태그)가 암살자이거나 전사인데 묶기·딜이 높은 챔피언.
    # 베인(원딜)·신드라(마법사)처럼 보조 태그에만 암살자가 붙은 챔피언은 빼요 (Data Dragon 태그가 거칠어서)
    main = lambda c: (tags(c) or ("",))[0]  # noqa: E731
    e_divers = [c for c in enemies if T(c) and (main(c) == "Assassin" or (main(c) == "Fighter" and T(c)["engage"] >= 0.6 and T(c)["dmg_share"] >= 0.2))]
    front_us = [c for c in allies if T(c) and T(c)["taken_share"] >= FRONT]
    ek = name(e_carry[1]) if e_carry else None

    # 1) 내 역할
    is_tank = mt["engage"] >= 0.7 and mt["taken_share"] >= FRONT
    is_assassin = (tags(me) or ("",))[0] == "Assassin" and not is_tank
    is_carry = mt["dmg_share"] >= CARRY and mt["taken_share"] < FRONT and not is_assassin
    if is_tank:
        add("내가 먼저 들어가서 묶어요. 묶은 다음엔 우리 딜러 앞으로 돌아와 막아요.",
            f"{josa(mn, '은는')} 상대를 묶은 기록이 챔피언 중 상위 {_pct_top(mt['engage'])}%이고, 팀이 받은 피해의 {mt['taken_share']:.0%}를 받아요. "
            f"오브젝트 앞 한타에서 첫 킬을 낸 팀이 드래곤을 {FK_DRAGON:.0%}, 바론을 {FK_BARON:.0%} 가져가는데, 첫 킬은 보통 묶인 사람에게서 나와요. "
            f"묶고 나서 뒤로 빠지면 우리 딜러가 상대 진입을 혼자 받아요.",
            "fact", trait_eid, fight_eid)
    elif is_assassin:
        tgt = f"{ek}" if ek else "상대 딜러"
        add(f"한타가 시작돼도 바로 들어가지 말고, 시야 밖 옆에서 기다렸다가 {tgt}에게 들어가요.",
            (f"{josa(mn, '은는')} 팀 딜의 {mt['dmg_share']:.0%}를 넣지만 맞아 주는 챔피언이 아니에요 (받은 피해 {mt['taken_share']:.0%}). "
             + (f"{josa(ek, '은는')} 상대 팀 딜의 {e_carry[0]:.0%}를 넣는 핵심 딜러라, 이 챔피언 하나를 먼저 지우면 상대는 남은 딜로 못 버텨요. " if ek else "")
             + f"처음부터 들어가면 상대 CC를 다 맞고 내가 먼저 죽어요. 정글이 먼저 죽으면 강타도 같이 사라져서 상대가 드래곤을 {JG_DEAD_DRAGON:.0%}, 바론을 {JG_DEAD_BARON:.0%} 가져가요."),
            "fact", trait_eid, fight_eid)
    elif is_carry:
        add("앞라인 뒤에서 닿는 적부터 치고, 상대 CC가 빠진 뒤에 들어가요.",
            f"{josa(mn, '은는')} 팀 딜의 {mt['dmg_share']:.0%}를 넣는 챔피언이라 내가 살아 있는 시간이 곧 우리 팀 딜이에요. "
            f"정글인 내가 먼저 죽으면 강타도 같이 사라져서 상대가 드래곤을 {JG_DEAD_DRAGON:.0%}, 바론을 {JG_DEAD_BARON:.0%} 가져가요.",
            "fact", trait_eid, fight_eid)
    else:
        add("우리 쪽으로 들어온 적부터 같이 잡아요. 상대 진영 깊이 혼자 들어가지 않아요.",
            f"{josa(mn, '은는')} 팀 딜 {mt['dmg_share']:.0%}, 받은 피해 {mt['taken_share']:.0%}로 딜과 버티기가 섞인 챔피언이에요. "
            f"들어온 적은 이미 우리 쪽 깊이 있어서 잡기 쉬워요. 반대로 내가 상대 진영 깊이 들어가 먼저 죽으면 강타가 같이 사라져서 "
            f"상대가 드래곤을 {JG_DEAD_DRAGON:.0%} 가져가요.", "fact", trait_eid, fight_eid)

    # 2) 상대 CC: 먼저 들어가지 않을 조건
    if e_cc:
        nm = "·".join(name(c) for c in e_cc[:3])
        best = max(T(c)["engage"] for c in e_cc)
        add(f"상대 {nm}의 진입·CC가 빠지기 전엔 먼저 몸을 보이지 않아요.",
            f"{josa(nm, '은는')} 상대를 묶은 기록이 챔피언 중 상위 {_pct_top(best)}% 안이에요. 오브젝트 앞에서 이 CC에 묶여 먼저 죽으면 "
            f"상대가 드래곤을 {FK_DRAGON:.0%} 가져가고, 그게 정글인 나라면 {JG_DEAD_DRAGON:.0%}예요. CC를 쓴 걸 본 다음이 우리가 들어갈 때예요.",
            "fact", trait_eid, fight_eid)

    # 3) 지킬 사람 (상대에 돌진·암살이 있을 때)
    if a_carry and e_divers and not is_assassin:
        ac, dv = name(a_carry[1]), "·".join(name(c) for c in e_divers[:2])
        add(f"한타에서 {ac} 옆을 지켜요. {josa(dv, '이가')} 들어오면 그 챔피언부터 같이 잡아요.",
            f"{josa(ac, '은는')} 우리 팀 딜의 {a_carry[0]:.0%}를 넣는 핵심 딜러예요. 상대 {josa(dv, '은는')} 뒤로 들어와 딜러를 노리는 챔피언이라, "
            f"{josa(ac, '이가')} 먼저 죽으면 우리 딜이 그만큼 빠지고 첫 킬도 내줘요.", "fact", trait_eid, fight_eid)

    # 4) 앞라인이 없으면 정면 한타를 피한다
    if len([c for c in front_us if c != me]) + (1 if is_tank else 0) == 0:
        add("정면 5:5 한타는 피하고, 시야로 한 명을 끊은 다음 오브젝트를 쳐요.",
            "우리 팀엔 피해를 받아 줄 앞라인이 없어요 (팀이 받은 피해 비중이 상위 25%인 챔피언이 없어요). 정면으로 붙으면 딜러가 먼저 맞아요. "
            f"오브젝트 앞에서 첫 킬을 낸 팀이 드래곤을 {FK_DRAGON:.0%}, 바론을 {FK_BARON:.0%} 가져가요.", "fact", trait_eid, fight_eid)

    # 5) 오브젝트 앞: 데이터로 본 '이기는 순서'
    pickers = [c for c in allies if T(c) and T(c)["pick"] >= 0.8]
    e_pickers = [c for c in enemies if T(c) and T(c)["pick"] >= 0.8]
    if pickers:
        pk = "·".join(name(c) for c in pickers[:2])
        add(f"드래곤·바론 1분 전에 {pk}로 시야 밖 한 명을 먼저 노려요.",
            f"{josa(pk, '은는')} 같이 끊는 킬이 챔피언 중 상위권이에요. 오브젝트 앞 첫 킬을 낸 팀이 드래곤을 {FK_DRAGON:.0%}, 바론을 {FK_BARON:.0%} 가져가요. "
            f"끊은 뒤엔 쫓지 말고 바로 오브젝트로 가요. 첫 킬 바로 다음 킬은 {SECOND_OTHER:.0%}가 상대 팀에서 나와요 (쫓다가 받아치기를 당해요).",
            "fact", trait_eid, fight_eid)
    elif e_pickers:
        pk = "·".join(name(c) for c in e_pickers[:2])
        add("오브젝트 앞 와드는 둘이 같이 박고, 혼자 시야 없는 곳에 들어가지 않아요.",
            f"상대 {josa(pk, '은는')} 같이 끊는 킬이 챔피언 중 상위권이에요. 오브젝트 앞에서 한 명이 먼저 잡히면 상대가 드래곤을 {FK_DRAGON:.0%} 가져가고, "
            f"잡힌 게 정글인 나라면 {JG_DEAD_DRAGON:.0%}예요.",
            "fact", trait_eid, fight_eid)
    return out
