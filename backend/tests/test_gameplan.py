from loldosa.briefing.gameplan import build_game_plan, team_profile


def test_comp_types_from_real_traits():
    assert team_profile([54, 64, 61, 145, 111])["type"] == "engage"      # 말파이트·리신·오리아나·카이사·노틸러스
    assert team_profile([115, 141, 74, 51, 350])["type"] == "poke"       # 직스·케인·하이머딩거·케이틀린·유미
    assert team_profile([23, 104, 4, 29, 40])["type"] == "split"         # 트린다미어 사이드
    assert team_profile([1, 2]) is None                                  # 성향 아는 챔피언 3명 미만


CTX = {
    "lanes": {"top": {"ally": "말파이트", "enemy": "피오라", "gd": -320, "n": 400, "eid": "E5"},
              "bot": {"ally": "카이사·노틸러스", "enemy": "이즈리얼·소라카", "gd": 260, "n": 300, "eid": "E6"}},
    "ejg": {"name": "카직스", "n": 200, "eid": "E7", "gank_lane": "bot", "gank_share": 0.5, "gank_s": 205,
            "invade": 20, "invade_base": 13, "fd": 0.62, "fd_base": 0.5, "fg": 0.4, "fg_base": 0.48},
    "late": {"ally": [("카이사", 0.05)], "enemy": [], "ally_sum": 0.04, "enemy_sum": 0.0, "eid": "E8"},
}


def test_plan_lines_come_from_this_games_facts_only():
    gp = build_game_plan([54, 64, 61, 145, 111], [114, 121, 101, 81, 16], {}, {}, str, "E1", "E2", CTX)
    keys = [p["key"] for p in gp["phases"]]
    assert keys == ["early", "objectives", "mid", "late"]
    early = gp["phases"][0]
    assert early["headline"].startswith("카직스는 첫 갱을 봇으로 50%")
    texts = [i["text"] for p in gp["phases"] for i in p["items"]]
    assert any("탑 말파이트 vs 피오라" in t and "밀리는" in t for t in texts)
    assert any("카정이 잦아요" in t for t in texts)
    assert any("봇 카이사·노틸러스(+260) 쪽이 이겨서 5:00 첫 드래곤" in t for t in texts)
    for banned in ("아타칸", "위업", "주도권이 있는 쪽", "라인별 차이는 크지 않아요"):
        assert all(banned not in t for t in texts)
    # 일반론만 남는 시간대는 통째로 빠진다
    bare = build_game_plan([54, 64, 61, 145, 111], [114, 121, 101, 81, 16], {}, {}, str, "E1", "E2", {})
    assert [p["key"] for p in bare["phases"]] == ["mid"]


def test_ai_prompt_gets_game_plan_and_drops_outdated_rules():
    from loldosa.coach.claude import build_prompt, parse_and_validate

    gp = build_game_plan([54, 64, 61, 145, 111], [114, 121, 101, 81, 16], {}, {}, str, "E1", "E2", CTX)
    prompt = build_prompt({"cards": [], "evidence": [], "game_plan": gp})
    assert "GAME_PLAN" in prompt and "5~15분" in prompt
    out = parse_and_validate('{"headline":"h","points":[{"phase":"20분~","text":"아타칸을 먼저 쳐요","evidence":["E1"]},'
                             '{"phase":"~5분","text":"풀캠 후 바위게","evidence":["E1"]}]}', {"E1"})
    assert [p["text"] for p in out["points"]] == ["풀캠 후 바위게"] and out["dropped"] == 1
