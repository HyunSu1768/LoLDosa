import asyncio

from loldosa.coach.claude import ClaudeCoach, build_prompt, parse_and_validate


def test_validate_drops_uncited_and_unknown():
    text = '''설명 {"headline": "h", "points": [
        {"phase": "0-3분", "text": "근거 있음", "evidence": ["E1", "E9"]},
        {"phase": "3-8분", "text": "근거 없음", "evidence": []},
        {"phase": "전체", "text": "없는 근거", "evidence": ["E77"]}]}'''
    r = parse_and_validate(text, {"E1", "E2"})
    assert r["headline"] == "h"
    assert [p["text"] for p in r["points"]] == ["근거 있음"]
    assert r["points"][0]["evidence"] == ["E1"]
    assert r["dropped"] == 2


def test_prompt_contains_evidence():
    b = {"my_champion_name": "리 신", "scope_label": "x", "cards": [],
         "evidence": [{"id": "E1", "text": "t", "games": 3, "confidence": "낮음", "source": "s"}]}
    p = build_prompt(b)
    assert '"E1"' in p and "리 신" in p


def test_coach_with_fake_cli(monkeypatch):
    coach = ClaudeCoach()
    coach.enabled = True

    async def fake(prompt):
        return '{"headline": "ok", "points": [{"phase": "전체", "text": "a", "evidence": ["E1"]}]}'

    monkeypatch.setattr(coach, "run_cli", fake)
    r = asyncio.run(coach.coach({"evidence": [{"id": "E1"}]}))
    assert r["status"] == "ok" and len(r["points"]) == 1


def test_coach_disabled():
    coach = ClaudeCoach()
    coach.enabled = False
    assert asyncio.run(coach.coach({}))["status"] == "disabled"
