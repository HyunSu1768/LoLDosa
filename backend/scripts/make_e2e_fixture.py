"""CI 용 전체 흐름 검증 데이터: 통계 묶음 + 고정 경기 1판(tests/fixtures/match1)을 '내 경기'로 넣은 데이터 폴더.

사용: python scripts/make_e2e_fixture.py <out_data_dir> [keyless]   → 마지막 줄에 game_id 출력
keyless: 내 경기 DB·Riot ID 없이 (롤 클라이언트 전적에서 받아야 하는 상황)
"""
import gzip
import json
import sys
from pathlib import Path

from loldosa.bundle import install
from loldosa.review.sync import PERSONAL_DB
from loldosa.settings import UserSettings
from loldosa.store.matches import MatchStore

ROOT = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
install(out, force=True, bdir=ROOT.parent / "bundle")
d = json.load(gzip.open(ROOT / "tests" / "fixtures" / "match1.json.gz", "rt", encoding="utf-8"))
m, tl = d["match"], d["timeline"]
keyless = len(sys.argv) > 2 and sys.argv[2] == "keyless"
jg = next(p for p in m["info"]["participants"] if p["teamPosition"] == "JUNGLE")
if not keyless:
    store = MatchStore(out, filename=PERSONAL_DB)
    store.save_raw(m["metadata"]["matchId"], m, tl)
    store.ingest(m, tl, "personal")
    store.close()
us = UserSettings.load(out)
us.update({"riot_id": "" if keyless else "fixture#KR1", "puuid": "" if keyless else jg["puuid"], "onboarded": True}).save(out)
print(m["metadata"]["matchId"].split("_")[1])
