"""익명화한 실제 경기 3개로 수집 저장 → 통계 빌드 → 브리핑까지 통합 테스트."""

import gzip
import json
from pathlib import Path

import pytest
from champselect_builder import sequence

from loldosa.analysis.build import build_stats
from loldosa.analysis.geometry import nearest_camp, region, relative_region
from loldosa.analysis.query import Scope, StatsDB
from loldosa.briefing.engine import BriefingEngine, josa
from loldosa.ddragon import Champion, ChampionIndex
from loldosa.lcu.champselect import parse_session
from loldosa.store.matches import MatchStore

FIX = Path(__file__).parent / "fixtures"


def fixtures():
    for p in sorted(FIX.glob("match*.json.gz")):
        with gzip.open(p, "rt") as f:
            d = json.load(f)
        yield d["match"], d["timeline"]


def champ_index(ids) -> ChampionIndex:
    return ChampionIndex("test", {i: Champion(i, f"C{i}", f"챔프{i}", ("Fighter",), 5, 5, 5) for i in ids})


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    d = tmp_path_factory.mktemp("data")
    store = MatchStore(d)
    ids = set()
    for match, timeline in fixtures():
        store.ingest(match, timeline, "apex")
        ids |= {p["championId"] for p in match["info"]["participants"]}
    counts = store.counts()
    store.close()
    champs = champ_index(ids | {64, 266, 103, 222, 412, 24, 203, 134, 81, 497})
    build_stats(d, champs)
    return d, champs, counts


def test_ingest_counts(built):
    _, _, counts = built
    assert counts["matches"] == 3


def test_ingest_idempotent(built, tmp_path):
    store = MatchStore(tmp_path)
    m, t = next(fixtures())
    store.ingest(m, t, "apex")
    store.ingest(m, t, "apex")
    assert store.counts()["matches"] == 1
    assert store._x("SELECT count(*) FROM participants")[0][0] == 10
    store.close()


def test_stats_tables(built):
    d, _, _ = built
    stats = StatsDB(d / "stats.duckdb")
    with stats.session():
        s = Scope("ALL", "apex")
        assert stats.matches(s) == 3
        pool = stats.jungle_pool(s, min_games=1)
        assert sum(p["games"] for p in pool) == 6  # 경기당 정글러 2명
        assert all(0 <= p["win_rate_adj"] <= 1 for p in pool)
        assert stats.objectives(s)["matches"] == 3


def test_briefing_evidence_integrity(built):
    d, champs, _ = built
    engine = BriefingEngine(StatsDB(d / "stats.duckdb"), champs)
    for raw in sequence():
        if raw is None:
            continue
        state = parse_session(raw)
        b = engine.build(state).to_dict()
        ids = {e["id"] for e in b["evidence"]}
        for card in b["cards"]:
            assert card["headline"]
            for item in card["items"]:
                assert set(item["evidence"]) <= ids
                if item["kind"] == "inference":
                    assert item["evidence"], item["text"]
        unavailable = set(state.ally_bans) | set(state.enemy_bans) | {
            x.champion_id for x in state.allies + state.enemies if x.locked}
        assert not {p["champion_id"] for p in b["picks"]} & unavailable
        for r in b["picks"] + b["bans"]:
            for it in r["reasons"]:
                assert it["evidence"] and set(it["evidence"]) <= ids


def test_no_stats_db(tmp_path):
    engine = BriefingEngine(StatsDB(tmp_path / "missing.duckdb"), champ_index([64]))
    b = engine.build(parse_session(sequence()[0]))
    assert b.notes and not b.cards


def test_geometry():
    assert region(1000, 8000) == "top"
    assert region(8000, 1000) == "bot"
    assert region(7400, 7400) == "mid"
    assert region(4400, 9600) == "river"
    assert region(500, 500) == "base"
    assert relative_region(100, 3800, 7900) == "own_jungle"
    assert relative_region(200, 3800, 7900) == "enemy_jungle"
    assert nearest_camp(100, 3700, 7800) == "blue"
    assert nearest_camp(200, 14870 - 3700, 14870 - 7800) == "blue"


def test_josa():
    assert josa("리 신") == "리 신은"
    assert josa("아리") == "아리는"
    assert josa("잭스", "이가") == "잭스가"


def test_insights_card_uses_guides(built):
    from loldosa.sources.guides import GuideKB, SourceDoc

    d, champs, _ = built
    kb = GuideKB(d)
    src = SourceDoc("text", "https://example.com/g", "가이드", "저자", "ko", "리 신은 레드에서 시작합니다")
    kb.save(src, [{"champion_id": 64, "vs_champion_id": 0, "topic": "route", "text": "레드 시작",
                   "quote": "리 신은 레드에서 시작합니다", "start_s": None, "url": src.url}])
    engine = BriefingEngine(StatsDB(d / "stats.duckdb"), champs, kb.path)
    b = engine.build(parse_session(sequence()[-2]))
    card = next(c for c in b.cards if c.id == "insights")
    guide_items = [i for i in card.items if i.kind == "guide"]
    assert guide_items and "레드 시작" in guide_items[0].text
    ev = {e.id: e for e in b.evidence}
    assert ev[guide_items[0].evidence[0]].url == "https://example.com/g"
