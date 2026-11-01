"""판단 훈련: 상황 추출·행동 분류·비슷한 상황 찾기."""

import duckdb
from test_pipeline import fixtures

from loldosa.analysis.decisions import ACTIONS, build_states, jungler_states, load_match, similar, summarize, to_vector
from loldosa.store.matches import MatchStore


def _store(tmp_path):
    st = MatchStore(tmp_path)
    for m, t in fixtures():
        st.ingest(m, t, "apex")
    return st


def test_states_and_actions(tmp_path):
    st = _store(tmp_path)
    mid = st._x("SELECT match_id FROM matches LIMIT 1")[0][0]
    md = load_match(st.con, mid)
    rows = jungler_states(md)
    assert rows and all(r["action"] in ACTIONS for r in rows)
    assert {r["minute"] for r in rows} <= set(range(2, 21))
    assert all(len(to_vector(r)) == 19 for r in rows)
    st.close()


def test_similar_and_summary(tmp_path):
    st = _store(tmp_path)
    path = st.path
    st.close()
    con = duckdb.connect()
    con.execute(f"ATTACH '{path}' AS src (READ_ONLY)")
    from loldosa.analysis.decisions import STATE_COLUMNS
    rows = [dict(zip(STATE_COLUMNS, r)) for r in build_states(con, "src.")]
    assert rows
    q = dict(rows[0])
    neigh = similar(rows, q, k=10)
    assert neigh and neigh[0]["_dist"] == 0.0
    summ = summarize(neigh)
    assert abs(sum(s["share"] for s in summ) - 1.0) < 1e-9


def test_score_actions_prefers_outcome_over_popularity():
    from loldosa.review.moments import score_actions

    crowd = [{"action": "farm", "share": 0.5, "n": 30, "swing": -300, "died": 0.1, "obj": 0},
             {"action": "recall", "share": 0.2, "n": 12, "swing": 200, "died": 0.0, "obj": 0},
             {"action": "invade", "share": 0.05, "n": 3, "swing": 2000, "died": 0.0, "obj": 0}]  # 표본 적음 → 판정 제외
    # 정답은 인기(20%↑) 기준 (검증에서 실력을 가장 잘 가름), 결과 1위는 참고 배지
    assert score_actions(crowd) == ["farm", "recall"]
    assert crowd[1]["best"] is True and crowd[2]["score"] is None and crowd[0]["best"] is False


def test_last_seen_uses_only_past_exact_events():
    from types import SimpleNamespace

    from loldosa.review.moments import last_seen

    ev = [{"ts_ms": 100_000, "type": "CHAMPION_KILL", "participant_id": 7, "victim_id": 2, "assists": [], "x": 1000, "y": 2000},
          {"ts_ms": 150_000, "type": "CHAMPION_KILL", "participant_id": 3, "victim_id": 4, "assists": [7], "x": 5000, "y": 6000},
          {"ts_ms": 400_000, "type": "ELITE_MONSTER_KILL", "participant_id": 7, "victim_id": None, "assists": None, "x": 9000, "y": 4000}]
    md = SimpleNamespace(events=ev)
    s = last_seen(md, 7, 180_000)
    assert (s["t"], s["x"], s["ago"]) == (150, 5000, 30)   # 판단 시점 뒤 사건은 쓰지 않는다
    assert last_seen(md, 9, 180_000) is None


def test_story_and_after_follow_time():
    from types import SimpleNamespace

    from loldosa.analysis.turns import ShopVisit
    from loldosa.review.moments import _merged, after, story

    parts = {1: {"team": 100, "position": "JUNGLE", "champion_id": 0, "puuid": "me"},
             6: {"team": 200, "position": "JUNGLE", "champion_id": 0, "puuid": "x"}}
    frames = {(q, m): {"x": 3000 + m * 100, "y": 7000, "level": 3, "gold": 0, "jcs": m * 8, "cur": 0, "hp": 1, "hp_max": 1}
              for q in (1, 6) for m in range(0, 8)}
    ev = [{"ts_ms": 4 * 60_000 + 52_000, "type": "CHAMPION_KILL", "participant_id": 1, "victim_id": 6, "assists": [],
           "team_id": None, "monster_type": None, "x": 9000, "y": 9000},
          *[{"ts_ms": 6 * 60_000 + i * 6000, "type": "ELITE_MONSTER_KILL", "participant_id": 6, "victim_id": None, "assists": [],
             "team_id": 200, "monster_type": "HORDE", "x": 5000, "y": 10000} for i in range(3)]]
    md = SimpleNamespace(parts=parts, frames=frames, events=ev)
    champs = SimpleNamespace(get=lambda _c: None)
    visits = [ShopVisit(1, 3 * 60_000 + 34_000, False)]
    st = story(md, champs, 1, 6, 100, 5, visits)
    assert st["head"].startswith("3:34에 귀환했다가") and "16개" in st["head"]
    assert [round(i["t"]) for i in st["items"]] == sorted(round(i["t"]) for i in st["items"])
    steps = after(md, champs, 1, 6, 100, 5, visits)
    texts = [s["text"] for s in steps]
    assert texts[0] == "이 순간 실제 위치예요" and texts[-1] == "2분 뒤 위치예요"
    assert any("공허 유충 3마리" in t for t in texts)
    assert len(_merged(ev)) == 2
