"""배포용 통계 만들기: 보관된 원본(raw)에서 티어별로 경기를 모아 새 matches.duckdb 를 만들고 analyze 한다.

사용: python scripts/build_production_stats.py <raw_dir> <out_data_dir> <bucket>=<duckdb 또는 players.json> ...
예:   apex=/tmp/val/matches.duckdb apex=/tmp/val/pro_players.json platinum=/tmp/val/plat_group.json
그다음: LOLDOSA_DATA_DIR=<out_data_dir> loldosa analyze && loldosa bundle export
"""
import gzip
import json
import sys
from pathlib import Path

import duckdb

from loldosa.store.matches import MatchStore


def match_ids(src: str) -> list[str]:
    if src.endswith(".duckdb"):
        con = duckdb.connect(src, read_only=True)
        ids = [r[0] for r in con.execute("SELECT match_id FROM matches").fetchall()]
        con.close()
        return ids
    d = json.loads(Path(src).read_text())
    return [m for v in d.values() for m in (v["matches"] if isinstance(v, dict) else v)]


def main():
    raw, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    store = MatchStore(out)
    done: set[str] = set()
    for arg in sys.argv[3:]:
        bucket, src = arg.split("=", 1)
        n = 0
        for mid in match_ids(src):
            if mid in done:
                continue
            p = raw / f"{mid}.json.gz"
            if not p.exists():
                continue
            with gzip.open(p, "rt", encoding="utf-8") as f:
                d = json.load(f)
            store.save_raw(mid, d["match"], d["timeline"])
            store.ingest(d["match"], d["timeline"], bucket)
            done.add(mid)
            n += 1
        print(bucket, src, n, flush=True)
    store.close()


main()
