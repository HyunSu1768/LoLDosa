from loldosa.briefing.gameplan import build_game_plan, team_profile


def test_comp_types_from_real_traits():
    assert team_profile([54, 64, 61, 145, 111])["type"] == "engage"      # 말파이트·리신·오리아나·카이사·노틸러스
    assert team_profile([115, 141, 74, 51, 350])["type"] == "poke"       # 직스·케인·하이머딩거·케이틀린·유미
    assert team_profile([23, 104, 4, 29, 40])["type"] == "split"         # 트린다미어 사이드
    assert team_profile([1, 2]) is None                                  # 성향 아는 챔피언 3명 미만


def test_plan_has_four_phases_and_2026_rules_only():
    gp = build_game_plan([54, 64, 61, 145, 111], [114, 121, 101, 81, 16], {}, {}, str, "E1", "E2")
    assert [p["key"] for p in gp["phases"]] == ["early", "objectives", "mid", "late"]
    text = " ".join(i["text"] + p["headline"] for p in gp["phases"] for i in p["items"])
    for banned in ("아타칸", "위업", "14:00에 방패", "장로 드래곤은 15:00"):
        assert banned not in text
    assert all(i["evidence"] == ["E1"] for p in gp["phases"] for i in p["items"] if i["kind"] == "rule")
    assert gp["vs"] and gp["them"]["type"] == "split"


def test_ai_prompt_gets_game_plan_and_drops_outdated_rules():
    from loldosa.coach.claude import build_prompt, parse_and_validate

    gp = build_game_plan([54, 64, 61, 145, 111], [114, 121, 101, 81, 16], {}, {}, str, "E1", "E2")
    prompt = build_prompt({"cards": [], "evidence": [], "game_plan": gp})
    assert "GAME_PLAN" in prompt and "5~15분" in prompt
    out = parse_and_validate('{"headline":"h","points":[{"phase":"20분~","text":"아타칸을 먼저 쳐요","evidence":["E1"]},'
                             '{"phase":"~5분","text":"풀캠 후 바위게","evidence":["E1"]}]}', {"E1"})
    assert [p["text"] for p in out["points"]] == ["풀캠 후 바위게"] and out["dropped"] == 1
