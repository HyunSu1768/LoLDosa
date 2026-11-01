"""같은 플레이어 안에서 비교: 지표가 '자기 평소보다 좋았던 판'에 더 이겼나?

티어 비교(AUC)는 '고수가 원래 그렇다'는 상관일 수 있다. 같은 사람의 판끼리 비교하면 사람마다 다른 실력·챔프폭 차이가 빠져서
'이 지표를 올리면 이기는 판이 늘어나는지'에 한 걸음 더 가까워진다 (여전히 인과는 아님: 이기는 판이라 지표가 좋아질 수도 있음).

사용: python scripts/within_player.py <raw_dir> <matches.duckdb> [min_games=6]
결과: src/loldosa/learn/gap_reference.json 의 features[key]["within"] = {players, games, win_diff}
"""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

import duckdb

from loldosa.analysis.gap import BY_KEY, REFERENCE_PATH, jungler_features

raw, db = Path(sys.argv[1]), sys.argv[2]
min_games = int(sys.argv[3]) if len(sys.argv) > 3 else 6
con = duckdb.connect(db, read_only=True)
# 수집 때 시드로 쓴 플레이어(여러 판이 모인 사람)만: players 테이블의 puuid
seeds = {r[0] for r in con.execute("SELECT puuid FROM players").fetchall()}
pairs = con.execute("SELECT puuid, match_id FROM participants WHERE position='JUNGLE'").fetchall()
con.close()
by_player: dict[str, list] = defaultdict(list)
for pu, mid in pairs:
    if pu in seeds:
        by_player[pu].append(mid)
by_player = {k: v for k, v in by_player.items() if len(v) >= min_games}
print("players", len(by_player), "games", sum(len(v) for v in by_player.values()), flush=True)

rows: dict[str, list] = defaultdict(list)
for pu, mids in by_player.items():
    for mid in mids:
        p = raw / f"{mid}.json.gz"
        if not p.exists():
            continue
        d = json.load(gzip.open(p, "rt", encoding="utf-8"))
        f = jungler_features(d["match"], d["timeline"], pu)
        if f:
            rows[pu].append(f)

ref = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
for key, r in ref["features"].items():
    if key not in BY_KEY:
        continue
    hb = r["higher_better"]
    diffs, w, games = [], [], 0
    for pu, fs in rows.items():
        vals = [x for x in fs if x.get(key) is not None]
        if len(vals) < min_games:
            continue
        med = sorted(x[key] for x in vals)[len(vals) // 2]
        good = [x["win"] for x in vals if (x[key] > med if hb else x[key] < med)]
        bad = [x["win"] for x in vals if (x[key] < med if hb else x[key] > med)]
        if len(good) >= 2 and len(bad) >= 2:
            diffs.append(sum(good) / len(good) - sum(bad) / len(bad))
            w.append(len(vals))
            games += len(vals)
    if diffs:
        win_diff = sum(d * k for d, k in zip(diffs, w)) / sum(w)
        r["within"] = {"players": len(diffs), "games": games, "win_diff": round(win_diff, 3)}
        print(f"{key:15} players {len(diffs):4} games {games:5} 자기 평소보다 좋았던 판 승률 차 {win_diff:+.1%}", flush=True)
REFERENCE_PATH.write_text(json.dumps(ref, ensure_ascii=False, indent=1), encoding="utf-8")
