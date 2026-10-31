import asyncio

import pytest

from loldosa.sources.guides import (GuideKB, SourceDoc, extract, locate, validate_claims, youtube_id)
from loldosa.sources.pro import norm, to_records


def doc(segments=None):
    text = "리 신은 레드에서 시작해서 칼날부리를 먹고 3분 15초쯤 스커틀을 확인합니다. 킨드레드 상대로는 2레벨부터 압박합니다."
    return SourceDoc("youtube" if segments else "text", "https://www.youtube.com/watch?v=abcdefghijk",
                     "t", "a", "ko", text if not segments else " ".join(t for _, t in segments), segments)


def test_youtube_id():
    assert youtube_id("https://www.youtube.com/watch?v=abcdefghijk&t=3") == "abcdefghijk"
    assert youtube_id("https://youtu.be/abcdefghijk") == "abcdefghijk"
    assert youtube_id("https://www.youtube.com/shorts/abcdefghijk") == "abcdefghijk"
    with pytest.raises(ValueError):
        youtube_id("https://example.com/")


def test_locate_ignores_spacing_and_punctuation():
    found, start = locate(doc(), "칼날부리를  먹고, 3분 15초쯤")
    assert found and start is None
    assert locate(doc(), "바론을 먼저 칩니다")[0] is False


def test_locate_timestamp():
    segs = [(0.0, "리 신은 레드에서 시작해서"), (4.5, "칼날부리를 먹고 3분 15초쯤"), (9.0, "스커틀을 확인합니다.")]
    found, start = locate(doc(segs), "칼날부리를 먹고 3분 15초쯤 스커틀")
    assert found and start == 4.5


def test_validate_drops_fabricated_quotes():
    raw = [
        {"champion": "Lee Sin", "vs": "Kindred", "topic": "matchup", "text": "2렙 압박", "quote": "킨드레드 상대로는 2레벨부터 압박합니다"},
        {"champion": "Lee Sin", "topic": "route", "text": "지어낸 말", "quote": "블루에서 시작하고 바로 탑 갱"},
        {"champion": None, "topic": "weird", "text": "주제 이상", "quote": "스커틀을 확인합니다"},
    ]
    ok, dropped = validate_claims(doc(), raw, lambda n: {"Lee Sin": 64, "Kindred": 203}.get(n, 0))
    assert dropped == 1
    assert ok[0]["champion_id"] == 64 and ok[0]["vs_champion_id"] == 203
    assert ok[1]["topic"] == "general" and ok[1]["champion_id"] == 0


def test_extract_and_save(tmp_path):
    class FakeCoach:
        async def run_cli(self, prompt, system=None):
            assert "<<<" in prompt
            return '{"claims": [{"champion": "Lee Sin", "vs": null, "topic": "route", "text": "레드 시작", "quote": "레드에서 시작해서"}]}'

    d = doc()
    claims, dropped = asyncio.run(extract(d, FakeCoach(), lambda n: 64, say=lambda *_: None))
    assert len(claims) == 1 and dropped == 0
    kb = GuideKB(tmp_path)
    kb.save(d, claims)
    kb.save(d, claims)  # 같은 출처 재저장 시 중복 없음
    con = kb.connect(read_only=True)
    assert con.execute("SELECT count(*) FROM guide_claims").fetchall()[0][0] == 1
    con.close()
    assert kb.has_source(d.url)


def test_pro_records():
    row = {"game_id": "G1", "champion": "Lee Sin", "win": "Yes", "team": "T1", "player": "P",
           "tournament": "LCK 2026", "overview": "LCK/2026 Season", "patch": "16.20", "played_at": "2026-10-01 10:00:00",
           "minutes": "31.5", "team1": "Gen.G", "team2": "T1",
           "t1_dragons": "1", "t2_dragons": "3", "t1_grubs": "0", "t2_grubs": "3",
           "t1_heralds": "0", "t2_heralds": "1", "t1_barons": "0", "t2_barons": "1", "t1_atakhans": "", "t2_atakhans": "1"}
    rec = to_records([row], {norm("Lee Sin"): 64})[0]
    assert rec[4] == 64 and rec[5] is True
    assert rec[11:] == (3, 1, 3, 0, 1, 1, 1)  # T1 은 team2 쪽
