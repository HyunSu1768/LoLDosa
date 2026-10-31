import random

from loldosa.analysis.gap import auc, build_reference, champ_adjust, personal_gap


def rows(n, cs_mu, ping_mu, win_rate, champ=64, seed=0):
    r = random.Random(seed)
    return [{"jcs10": r.gauss(cs_mu, 5), "missing_pings": max(0, round(r.gauss(ping_mu, 2))),
             "deaths10": r.choice([0, 1, 2]), "win": r.random() < win_rate, "champion_id": champ} for _ in range(n)]


def test_auc_basic():
    assert auc(list(range(20, 40)), list(range(0, 20))) == 1.0
    assert abs(auc(list(range(20)), list(range(20))) - 0.5) < 1e-9


def test_reference_keeps_only_features_that_separate_in_wins_and_losses():
    groups = {"apex": rows(200, 72, 8, 0.5, seed=1), "platinum": rows(120, 62, 1, 0.5, seed=2)}
    ref = build_reference(groups, ("apex",), "platinum")
    f = ref["features"]
    assert f["jcs10"]["validated"] and f["jcs10"]["higher_better"]
    assert f["missing_pings"]["validated"]
    assert not f["deaths10"]["validated"]  # 무작위 → 못 가름


def test_personal_gap_ranks_biggest_shortfall_first():
    groups = {"apex": rows(200, 72, 8, 0.5, seed=1), "challenger": rows(80, 74, 8, 0.6, seed=3),
              "platinum": rows(120, 62, 1, 0.5, seed=2)}
    ref = build_reference(groups, ("challenger", "apex"), "platinum")
    me = rows(10, 73, 1, 0.5, seed=4)  # CS 는 고수급, 핑은 플래티넘급
    g = personal_gap(me, ref)
    assert g["gaps"][0]["key"] == "missing_pings"
    assert any(x["key"] == "jcs10" for x in g["strengths"])
    assert 0 <= g["progress"] <= 120


def test_champion_offset():
    ref = {"champ_offset": {"jcs10": {"64": 3.0}}}
    assert champ_adjust({"jcs10": 70, "champion_id": 64}, "jcs10", ref) == 67
    assert champ_adjust({"jcs10": 70, "champion_id": 1}, "jcs10", ref) == 70
