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
