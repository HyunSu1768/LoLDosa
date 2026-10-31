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
