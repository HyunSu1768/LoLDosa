from champselect_builder import BANS, LOCAL_CELL, PICKS, sequence

from loldosa.lcu.champselect import Stage, parse_session


def states():
    return [parse_session(s) for s in sequence() if s is not None]


def test_stage_progression():
    stages = [s.stage for s in states()]
    assert stages[0] == Stage.PLANNING
    assert stages[1] == Stage.BANNING
    # B0 픽, R5/R6 픽, 그리고 내 그룹(B1,B2) 진행 중 → 아직 내 픽 전
    assert stages[2:5] == [Stage.PRE_MY_PICK] * 3
    # 내 픽 확정 이후
    assert stages[5:7] == [Stage.POST_MY_PICK] * 2
    assert stages[-1] == Stage.FINAL


def test_me_and_jungle():
    first = states()[0]
    assert first.local_cell_id == LOCAL_CELL
    assert first.is_jungle
    assert first.me.intent_id == PICKS[LOCAL_CELL]
    assert first.me.shown_champion == PICKS[LOCAL_CELL]
    assert not first.me.locked


def test_final_state_has_all_picks_and_bans():
    final = states()[-1]
    assert [s.champion_id for s in final.allies] == [PICKS[c] for c in range(5)]
    assert [s.champion_id for s in final.enemies] == [PICKS[c] for c in range(5, 10)]
    assert all(s.locked for s in final.allies + final.enemies)
    assert final.ally_bans == tuple(BANS[c] for c in range(5))
    assert final.enemy_bans == tuple(BANS[c] for c in range(5, 10))


def test_enemy_jungle_spells_visible_after_lock():
    final = states()[-1]
    enemy_jg = next(s for s in final.enemies if s.cell_id == 6)
    assert 11 in enemy_jg.spells  # 강타


def test_signature_ignores_timer():
    a = sequence()[3]
    b = dict(a, timer={"phase": a["timer"]["phase"], "adjustedTimeLeftInPhase": 1})
    assert parse_session(a).signature() == parse_session(b).signature()


def test_bans_from_bans_field_when_actions_missing():
    s = sequence()[-2]
    s = dict(s, actions=[])
    st = parse_session(s)
    assert st.ally_bans == tuple(BANS[c] for c in range(5))
