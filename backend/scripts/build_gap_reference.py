"""챌린저 갭 기준표 만들기: 그룹별 정글러 지표 → AUC(이긴 판·진 판 분리) → src/loldosa/learn/gap_reference.json

사용: python scripts/build_gap_reference.py <raw_dir> <out.json> <group>=<players.json> ... [apex=<matches.duckdb>]
players.json: {puuid: [match_id, ...]}  /  apex=<duckdb>: 그 DB 경기의 정글러 전원 (고티어 표본)
고수 그룹: pro, challenger, apex  · 비교 그룹: platinum
"""
import gzip
import json
import sys
from pathlib import Path

import duckdb

from loldosa.analysis.gap import build_reference, jungler_features


def load(raw: Path, mid: str):
    p = raw / f"{mid}.json.gz"
    if not p.exists():
        return None
    with gzip.open(p, "rt", encoding="utf-8") as f:
        d = json.load(f)
    return d["match"], d["timeline"]


def main():
    raw, out = Path(sys.argv[1]), Path(sys.argv[2])
    groups, seen = {}, set()
    for arg in sys.argv[3:]:
        name, path = arg.split("=", 1)
        rows = []
        if path.endswith(".duckdb"):
            con = duckdb.connect(path, read_only=True)
            pairs = con.execute("SELECT puuid, match_id FROM participants WHERE position='JUNGLE'").fetchall()
            con.close()
        else:
            pairs = [(pu, m) for pu, ms in json.loads(Path(path).read_text()).items() for m in ms]
        for pu, mid in pairs:
            if (pu, mid) in seen:
                continue
            d = load(raw, mid)
            if not d:
                continue
            f = jungler_features(d[0], d[1], pu)
            if f:
                seen.add((pu, mid))
                rows.append(f)
        groups.setdefault(name, []).extend(rows)
        print(name, len(rows), flush=True)
    high = tuple(g for g in ("pro", "challenger", "apex") if g in groups)
    ref = build_reference(groups, high, "platinum")
    out.write_text(json.dumps(ref, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in sorted(ref["features"].items(), key=lambda kv: -kv[1]["auc"]):
        g = v["groups"]
        print(f"{k:15} auc {v['auc']:.2f} (win {v['auc_win']}, loss {v['auc_loss']}) {'✅' if v['validated'] else '  '} "
              + " ".join(f"{n}={x['median']}" for n, x in g.items()))


main()
