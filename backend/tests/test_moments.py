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
