from loldosa.analysis.turns import shop_visits, team_turn


def test_shop_visits_cluster_and_death_back():
    purchases = [(1, 1_000), (1, 240_000), (1, 255_000), (1, 500_000), (2, 300_000)]
    deaths = [(1, 450_000)]
    v = shop_visits(purchases, deaths)
    assert [(x.participant_id, x.ts_ms, x.death_back) for x in v] == [
        (1, 240_000, False), (2, 300_000, False), (1, 500_000, True)]


def test_team_turn_categories():
    T = 500_000
    jg, bot = 1, 2
    late = shop_visits([(jg, T - 10_000)], [])
    assert team_turn(late, T, jg, [bot]) == "late"
    sync = shop_visits([(jg, T - 100_000), (bot, T - 90_000)], [])
    assert team_turn(sync, T, jg, [bot]) == "sync"
    alone = shop_visits([(jg, T - 100_000), (bot, T - 20_000)], [])
    assert team_turn(alone, T, jg, [bot]) == "jg_only"
    assert team_turn([], T, jg, [bot]) == "none"
