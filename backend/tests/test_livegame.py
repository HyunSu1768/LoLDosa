from loldosa.lcu.livegame import compact, summarize


def row(t, lvl=1, gold=500, cs=0, items=(1,), dead=False, k=0, a=0):
    return {"t": t, "lvl": lvl, "gold": gold, "cs": cs, "k": k, "d": 0, "a": a, "dead": dead, "items": list(items)}


def test_summarize_levels_shops_rich_idle():
    rows = [row(0), row(80, 2, cs=8), row(120, 3, cs=16), row(200, 3, gold=1300, cs=24),
            row(260, 4, gold=1400, cs=24), row(330, 4, gold=1500, cs=24), row(340, 4, gold=200, cs=24, items=(1, 3070)),
            row(400, 6, gold=300, cs=40)]
    s = summarize({"rows": rows})
    assert s["levels"] == {2: 80, 3: 120, 4: 260, 6: 400}
    assert s["shops"] == [{"t": 340, "spent": 1300, "dead": False}]
    assert s["rich_s"] == 140  # 200→340(구매) 동안 1,200골드 넘게 들고 있음
    assert s["idle"] == [{"from": 200, "to": 340}]  # 200~340 CS 안 오름


def test_compact_picks_active_player():
    data = {"activePlayer": {"riotId": "me#KR1", "level": 3, "currentGold": 812.4},
            "allPlayers": [{"riotId": "x#1", "scores": {}}, {"riotId": "me#KR1", "isDead": False,
                           "scores": {"creepScore": 20, "kills": 1, "deaths": 0, "assists": 0}, "items": [{"itemID": 1036}]}],
            "gameData": {"gameTime": 181.23}}
    assert compact(data) == {"t": 181.2, "lvl": 3, "gold": 812, "cs": 20, "k": 1, "d": 0, "a": 0, "dead": False, "items": [1036]}
