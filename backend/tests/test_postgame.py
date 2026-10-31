from loldosa.lcu.postgame import GameEndDetector


def sess(gid, q=420):
    return {"gameData": {"gameId": gid, "queue": {"id": q}}}


def test_detects_solo_game_end_once():
    d = GameEndDetector()
    assert d.feed("ChampSelect", None) is None
    assert d.feed("InProgress", sess(123)) is None
    assert d.feed("InProgress", sess(123)) is None
    assert d.feed("WaitingForStats", None) == {"game_id": 123, "queue_id": 420}
    assert d.feed("EndOfGame", None) is None
    # 재접속으로 같은 게임이 다시 InProgress → 끝나도 두 번 알리지 않음
    d.feed("Reconnect", sess(123))
    assert d.feed("EndOfGame", None) is None


def test_ignores_other_queues():
    d = GameEndDetector()
    d.feed("InProgress", sess(5, q=450))  # 칼바람
    assert d.feed("EndOfGame", None) is None


def test_diagnostic_champselect_is_replayable(tmp_path):
    """진단 기록의 챔선 파일을 --replay 로 그대로 다시 틀 수 있어야 한다."""
    import json
    from pathlib import Path

    from loldosa.lcu.postgame import diag_write
    from loldosa.lcu.replay import load_sessions

    sample = Path(__file__).resolve().parents[1] / "samples" / "champselect_ranked_jungle.jsonl"
    sessions = [json.loads(x) for x in sample.read_text(encoding="utf-8").splitlines() if x.strip()]
    for s in sessions:
        diag_write(tmp_path, "champselect", s)
    f = next(tmp_path.glob("champselect_*.jsonl"))
    assert load_sessions(f) == sessions
