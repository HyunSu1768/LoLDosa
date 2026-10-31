"""배포용 통계 만들기: 보관된 원본(raw)에서 티어별로 경기를 모아 새 matches.duckdb 를 만들고 analyze 한다.

사용: python scripts/build_production_stats.py <raw_dir> <out_data_dir> [--min-patch 16.19] <bucket>=<duckdb 또는 players.json> ...
--min-patch: 이 패치보다 오래된 경기는 뺀다 (오래 쉰 프로 계정의 옛 경기 등)
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
    bucket = None
    if "#" in src:  # matches.duckdb#platinum : 그 버킷 경기만
        src, bucket = src.split("#", 1)
    if src.endswith(".duckdb"):
        con = duckdb.connect(src, read_only=True)
        ids = [r[0] for r in con.execute("SELECT match_id FROM matches WHERE ? IS NULL OR bucket = ?",
                                         [bucket, bucket]).fetchall()]
        con.close()
        return ids
    d = json.loads(Path(src).read_text())
    return [m for v in d.values() for m in (v["matches"] if isinstance(v, dict) else v)]


def main():
    args = sys.argv[3:]
    min_patch = None
    if args and args[0] == "--min-patch":
        min_patch, args = tuple(int(x) for x in args[1].split(".")), args[2:]
    raw, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    store = MatchStore(out)
    done: set[str] = set()
    skipped = 0
    for arg in args:
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
            if min_patch:
                ver = tuple(int(x) for x in d["match"]["info"]["gameVersion"].split(".")[:2])
                if ver < min_patch:
                    skipped += 1
                    continue
            store.save_raw(mid, d["match"], d["timeline"])
            store.ingest(d["match"], d["timeline"], bucket)
            done.add(mid)
            n += 1
        print(bucket, src, n, "(옛 패치 제외 누적", skipped, ")", flush=True)
    store.close()


main()
