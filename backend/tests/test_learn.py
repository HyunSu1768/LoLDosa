import json

from loldosa.learn.library import CONCEPTS_PATH, REQUIRED_IDS, Progress, load_library
from loldosa.learn.skills import CHECKS, evaluate


def test_concept_library_integrity():
    lib = load_library()
    ids = {c["id"] for c in lib["concepts"]}
    assert REQUIRED_IDS <= ids, REQUIRED_IDS - ids
    assert set(CHECKS) <= ids
    cats = {c["id"] for c in lib["categories"]}
    seen_alias = {}
    for c in lib["concepts"]:
        assert c["category"] in cats
        assert c["title"] and c["summary"]
        assert set(c.get("related", [])) <= ids
        for q in c.get("quiz", []):
            assert 0 <= q["answer"] < len(q["choices"])
        for a in c.get("aliases", []):
            assert a not in seen_alias, f"alias {a} in {c['id']} and {seen_alias[a]}"
            seen_alias[a] = c["id"]


def test_engine_and_review_concepts_exist():
    from loldosa.briefing.engine import PLAN_CONCEPTS
    from loldosa.review.analyze import LESSON_CONCEPTS

    ids = {c["id"] for c in load_library()["concepts"]}
    for lst in list(PLAN_CONCEPTS.values()) + [x for _, x in LESSON_CONCEPTS]:
        assert set(lst) <= ids


def test_evaluate_checks():
    facts = {"camps3": 6, "full_clear_rate": 0.5, "cs10": 60, "cs10_bench": 64, "deaths10": 1, "risky_deaths10": 1,
             "obj_turns": {"DRAGON": {"turn": "late", "took": False}}, "vision_pm": 1.0, "vision_bench": 1.0}
    res = {c["concept"]: c["status"] for c in evaluate(facts)}
    assert res["full-clear"] == "pass"
    assert res["clear-efficiency"] == "pass"
    assert res["turn-tempo"] == "fail" and res["recall-timing"] == "fail"
    assert res["jungle-tracking"] == "fail"
    # 풀클을 잘 안 하는 챔피언은 4캠프면 통과
    assert {c["concept"]: c["status"] for c in evaluate({"camps3": 4, "full_clear_rate": 0.2})}["full-clear"] == "pass"
    assert {c["concept"]: c["status"] for c in evaluate({})}["vision-control"] == "na"


def test_progress_history_and_rates(tmp_path):
    p = Progress(tmp_path)
    checks = [{"concept": "full-clear", "status": "pass", "value": "", "goal": ""},
              {"concept": "vision-control", "status": "fail", "value": "", "goal": ""}]
    p.record_checks("KR_1", {"date": "2026-10-01"}, checks)
    p.record_checks("KR_2", {"date": "2026-10-02"}, [dict(checks[0], status="fail"), checks[1]])
    rates = p.skill_rates()
    assert rates["full-clear"] == {"pass": 1, "total": 2}
    assert [h["match_id"] for h in p.history("full-clear")] == ["KR_2", "KR_1"]
    p.flag({"full-clear"}, "KR_2")
    p.flag({"full-clear"}, "KR_2")
    lib = {"concepts": [{"id": "full-clear", "title": "풀클리어"}]}
    assert Progress(tmp_path).recommended(lib)[0]["count"] == 1


def test_mastery_combines_sources(tmp_path):
    p = Progress(tmp_path)
    assert p.mastery("full-clear")["score"] is None
    for i in range(4):
        p.record_checks(f"KR_{i}", {"date": f"2026-10-0{i + 1}"}, [{"concept": "full-clear", "status": "pass",
                                                                    "value": "", "goal": ""}], {"camps3": 6})
    p.record_quiz("full-clear", False)
    m = p.mastery("full-clear")
    assert 80 <= m["score"] < 100 and m["n"] == 5


def test_srs_boxes(tmp_path):
    p = Progress(tmp_path)
    p.schedule("quiz:full-clear", "quiz", {"concept": "full-clear"})
    assert [x["key"] for x in p.due_items()] == ["quiz:full-clear"]
    it = p.grade("quiz:full-clear", True)
    assert it["box"] == 1 and not p.due_items()
    it = p.grade("quiz:full-clear", False)
    assert it["box"] == 0


def test_baseline_and_effect(tmp_path):
    from loldosa.learn.library import effect_report, ladder_points

    p = Progress(tmp_path)
    for i, (d, st, win) in enumerate([("2026-10-01 10:00", "fail", False), ("2026-10-02 10:00", "fail", False),
                                      ("2026-10-05 10:00", "pass", True), ("2026-10-06 10:00", "pass", True)]):
        p.record_checks(f"KR_{i}", {"date": d, "win": win},
                        [{"concept": "full-clear", "status": st, "value": "", "goal": ""}], {"cs10": 50 + i})
    assert p.baseline(exclude="KR_3")["cs10"] == 51
    p.record_rank({"tier": "PLATINUM", "rank": "II", "leaguePoints": 40, "wins": 1, "losses": 1})
    ef = effect_report(p, "full-clear", "2026-10-04T00:00:00")
    assert ef["before"]["focus_pass"] == 0 and ef["after"]["focus_pass"] == 2 and ef["after"]["wins"] == 2
    assert ladder_points({"tier": "EMERALD", "rank": "IV", "lp": 0}) - ladder_points(
        {"tier": "PLATINUM", "rank": "I", "lp": 0}) == 100
