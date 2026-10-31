"""익명화 픽스처로 리뷰·플랜·챔프폭·설정 검증."""

import gzip
import json
from pathlib import Path

import pytest
from champselect_builder import sequence
from test_pipeline import champ_index, fixtures

from loldosa.analysis.build import build_stats
from loldosa.analysis.query import StatsDB
from loldosa.briefing.engine import BriefingEngine, josa
from loldosa.lcu.champselect import parse_session
from loldosa.review.analyze import Reviewer
from loldosa.review.sync import PERSONAL_DB, list_matches, split_riot_id
from loldosa.settings import UserSettings
from loldosa.store.matches import MatchStore


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    d = tmp_path_factory.mktemp("rv")
    main, personal = MatchStore(d), MatchStore(d, filename=PERSONAL_DB)
    ids = set()
    for m, t in fixtures():
        main.ingest(m, t, "apex")
        personal.ingest(m, t, "personal")
        ids |= {p["championId"] for p in m["info"]["participants"]}
    main.close()
    champs = champ_index(ids | {64, 266, 103, 222, 412, 24, 203, 134, 81, 497})
    build_stats(d, champs)
    yield d, personal, champs
    personal.close()


def jungler_puuid(personal):
    return personal._x("SELECT puuid FROM participants WHERE position='JUNGLE' LIMIT 1")[0][0]


def test_review_jungle_match(env):
    d, personal, champs = env
    puuid = jungler_puuid(personal)
    games = list_matches(personal, puuid)
    assert games and games[0]["position"] == "JUNGLE"
    rv = Reviewer(personal, StatsDB(d / "stats.duckdb"), champs).review(games[0]["match_id"], puuid).to_dict()
    assert rv["is_jungle"]
    ids = {e["id"] for e in rv["evidence"]}
    for l in rv["lessons"] + rv["strengths"]:
        assert l["evidence"] and set(l["evidence"]) <= ids
    for m in rv["metrics"]:
        assert set(m["evidence"]) <= ids and m["verdict"] in ("good", "bad", "neutral")
    assert rv["paths"]["me"] and all(1 <= p[0] <= 10 for p in rv["paths"]["me"])
    assert any(m["kind"] == "start" for m in rv["moments"])
    severities = [l["severity"] for l in rv["lessons"]]
    assert severities == sorted(severities, reverse=True)


def test_review_non_jungle(env):
    d, personal, champs = env
    puuid = personal._x("SELECT puuid FROM participants WHERE position='TOP' LIMIT 1")[0][0]
    mid = list_matches(personal, puuid)[0]["match_id"]
    rv = Reviewer(personal, StatsDB(d / "stats.duckdb"), champs).review(mid, puuid)
    assert not rv.is_jungle and rv.notes and not rv.metrics


def test_review_unknown_match(env):
    d, personal, champs = env
    with pytest.raises(KeyError):
        Reviewer(personal, StatsDB(d / "stats.duckdb"), champs).review("KR_0", "x")


def test_split_riot_id():
    assert split_riot_id(" Hide on bush#KR1 ") == ("Hide on bush", "KR1")
    with pytest.raises(ValueError):
        split_riot_id("no-tag")


def test_plan_lines_have_evidence(env):
    d, _, champs = env
    engine = BriefingEngine(StatsDB(d / "stats.duckdb"), champs, settings=UserSettings())
    b = engine.build(parse_session(sequence()[-2])).to_dict()
    ids = {e["id"] for e in b["evidence"]}
    for line in b["plan"]:
        assert line["title"] and line["text"] and line["evidence"] and set(line["evidence"]) <= ids


def test_pool_restricts_picks(env):
    d, _, champs = env
    stats = StatsDB(d / "stats.duckdb")
    with stats.session():
        from loldosa.analysis.query import Scope
        pool_ids = [r["champion_id"] for r in stats.jungle_pool(Scope("ALL", "apex"), min_games=1)][:2]
    engine = BriefingEngine(stats, champs, settings=UserSettings(champion_pool=pool_ids))
    b = engine.build(parse_session(sequence()[2]))
    assert b.picks and all(r.in_pool for r in b.picks)
    assert all(not r.in_pool for r in b.picks_outside)


def test_settings_roundtrip(tmp_path):
    s = UserSettings.load(tmp_path)
    assert s.my_bucket == "platinum" and s.champion_pool == []
    s.update({"riot_id": "a#b", "champion_pool": [64], "unknown": 1}).save(tmp_path)
    s2 = UserSettings.load(tmp_path)
    assert s2.riot_id == "a#b" and s2.champion_pool == [64]


def test_josa_euro():
    assert josa("서폿", "으로") == "서폿으로"
    assert josa("정글", "으로") == "정글로"
    assert josa("미드", "으로") == "미드로"
