import gzip
import json
from pathlib import Path

from lcu_history_fixture import v5_to_lcu
from loldosa.lcu.matchhistory import to_v5
from loldosa.store.matches import MatchStore

FIX = Path(__file__).parent / "fixtures" / "match1.json.gz"


def test_lcu_history_roundtrip_reviews_like_riot_api(tmp_path):
    d = json.load(gzip.open(FIX, "rt", encoding="utf-8"))
    game, tl = v5_to_lcu(d["match"], d["timeline"])
    m5, t5 = to_v5(game, tl, "KR")
    assert m5["metadata"]["matchId"] == d["match"]["metadata"]["matchId"]
    orig = {p["participantId"]: p["teamPosition"] for p in d["match"]["info"]["participants"]}
    conv = {p["participantId"]: p["teamPosition"] for p in m5["info"]["participants"]}
    assert [k for k, v in orig.items() if v == "JUNGLE"] == [k for k, v in conv.items() if v == "JUNGLE"]  # 강타로 정글 판정
    store = MatchStore(tmp_path)
    store.ingest(m5, t5, "personal")
    n = store._x("SELECT count(*) FROM participants WHERE position = 'JUNGLE'")[0][0]
    store.close()
    assert n == 2
