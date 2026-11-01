from loldosa.coach.claude import build_weekly_prompt, parse_and_validate, weekly_evidence


def test_weekly_evidence_and_validation():
    gap = {"games": 12, "gaps": [{"label": "10분 정글 CS", "mine_text": "52개", "before_text": "48개", "platinum_text": "55개",
                                   "target_text": "68개", "games": 12, "lever": True, "if_then": "x"}], "strengths": []}
    skills = [{"title": "귀환 타이밍", "total": 5, "pass": 2}, {"title": "없음", "total": 0, "pass": 0}]
    ev = weekly_evidence(gap, skills, {"total": 6, "good": 4, "track_total": 3, "track_ok": 1})
    assert [e["id"] for e in ev] == ["G1", "S1", "D1"]
    assert "이전 48개" in ev[0]["text"] and "추적 3문제 중 1개" in ev[2]["text"]
    assert "G1" in build_weekly_prompt(gap, ev)
    out = parse_and_validate('{"headline":"h","points":[{"phase":"다짐","text":"a","evidence":["G1"]},'
                             '{"phase":"x","text":"b","evidence":["Z9"]}]}', {e["id"] for e in ev})
    assert len(out["points"]) == 1 and out["dropped"] == 1


def test_decision_summary(tmp_path):
    from loldosa.learn.library import Progress

    p = Progress(tmp_path)
    p.record_decision("M1", 5, "gank", True, ["ganking"], track_ok=False)
    p.record_decision("M1", 8, "farm", False, ["clear-efficiency"])
    s = p.decision_summary(7)
    assert s == {"total": 2, "good": 1, "track_total": 1, "track_ok": 0}
