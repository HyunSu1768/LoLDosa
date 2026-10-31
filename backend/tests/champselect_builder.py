"""랭크 솔로 챔선 세션(LCU 형식)을 단계별로 생성. 테스트와 샘플 녹화 파일에 쓴다.

블루 cell 0-4 / 레드 cell 5-9, 나는 블루 정글(cell 1, 블루 2픽).
픽 순서: B0 | R5 R6 | B1 B2 | R7 R8 | B3 B4 | R9
"""

from __future__ import annotations

import copy

POSITIONS = ["top", "jungle", "middle", "bottom", "utility"]
# 아군: 아트록스, 리 신, 아리, 징크스, 쓰레쉬 / 적: 잭스, 킨드레드, 신드라, 이즈리얼, 라칸
PICKS = {0: 266, 1: 64, 2: 103, 3: 222, 4: 412, 5: 24, 6: 203, 7: 134, 8: 81, 9: 497}
BANS = {0: 238, 1: 777, 2: 11, 3: 141, 4: 72, 5: 799, 6: 901, 7: 893, 8: 800, 9: 950}
PICK_ORDER = [[0], [5, 6], [1, 2], [7, 8], [3, 4], [9]]
LOCAL_CELL = 1


def _member(cell: int, ally: bool) -> dict:
    return {
        "cellId": cell,
        "assignedPosition": POSITIONS[cell % 5] if ally else "",
        "championId": 0,
        "championPickIntent": 0,
        "spell1Id": 4 if ally else 0,
        "spell2Id": 11 if ally and cell % 5 == 1 else (14 if ally else 0),
        "team": 1 if cell < 5 else 2,
    }


def base_session() -> dict:
    action_id = 0
    actions = []
    ban_group = []
    for cell in range(10):
        ban_group.append({"id": action_id, "actorCellId": cell, "championId": 0, "completed": False,
                          "isInProgress": False, "isAllyAction": cell < 5, "type": "ban"})
        action_id += 1
    actions.append(ban_group)
    for group in PICK_ORDER:
        g = []
        for cell in group:
            g.append({"id": action_id, "actorCellId": cell, "championId": 0, "completed": False,
                      "isInProgress": False, "isAllyAction": cell < 5, "type": "pick"})
            action_id += 1
        actions.append(g)
    return {
        "localPlayerCellId": LOCAL_CELL,
        "myTeam": [_member(c, True) for c in range(5)],
        "theirTeam": [_member(c, False) for c in range(5, 10)],
        "actions": actions,
        "bans": {"myTeamBans": [], "theirTeamBans": [], "numBans": 10},
        "timer": {"phase": "PLANNING", "adjustedTimeLeftInPhase": 10000},
    }


def sequence() -> list[dict | None]:
    """챔선 시작 → 밴 → 6개 픽 그룹 → 확정 → 종료(None)."""
    out: list[dict | None] = []
    s = base_session()
    # 1) 선픽 의도: 나는 리 신 의도 표시
    s["myTeam"][LOCAL_CELL]["championPickIntent"] = PICKS[LOCAL_CELL]
    out.append(copy.deepcopy(s))

    # 2) 밴 진행 → 밴 완료
    s["timer"]["phase"] = "BAN_PICK"
    for a in s["actions"][0]:
        a["isInProgress"] = True
    out.append(copy.deepcopy(s))
    for a in s["actions"][0]:
        a.update(isInProgress=False, completed=True, championId=BANS[a["actorCellId"]])
    s["bans"]["myTeamBans"] = [BANS[c] for c in range(5)]
    s["bans"]["theirTeamBans"] = [BANS[c] for c in range(5, 10)]

    # 3) 픽 그룹들
    for gi, group in enumerate(s["actions"][1:], start=1):
        for a in group:
            a["isInProgress"] = True
        out.append(copy.deepcopy(s))
        for a in group:
            cell = a["actorCellId"]
            a.update(isInProgress=False, completed=True, championId=PICKS[cell])
            team = s["myTeam"] if cell < 5 else s["theirTeam"]
            team[cell % 5]["championId"] = PICKS[cell]
            if cell >= 5 and cell % 5 == 1:
                team[cell % 5]["spell1Id"], team[cell % 5]["spell2Id"] = 4, 11

    # 4) 확정 단계 → 종료
    s["timer"]["phase"] = "FINALIZATION"
    out.append(copy.deepcopy(s))
    out.append(None)
    return out
