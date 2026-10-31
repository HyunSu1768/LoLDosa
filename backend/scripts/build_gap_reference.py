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


# 지표마다 리플레이에서 볼 시점 (초). 값 자체가 시각인 지표는 그 직전으로.
WATCH_AT = {"jcs10": 55, "cs15": 55, "first_recall": None, "lv6_time": None, "kp": 240, "dead_pct": 240,
            "vision_pm": 480, "ward_kills_pm": 480, "pings_pm": 150, "missing_pings": 150, "omw_pings": 150,
            "getback_pings": 150, "vision_pings": 300}


def exemplars(rows, ref, names, per=4):
    """프로 경기 중 그 지표를 가장 잘한 판 (선수 중복 없이). 같은 패치 동안 클라이언트에서 리플레이로 볼 수 있다."""
    out = {}
    for key, r in ref["features"].items():
        if not r["validated"]:
            continue
        # 극단값(예: 1:50 상점 구매, 핑 40번)은 따라 할 본보기가 아니라서, 프로 중앙값~상위 25% 사이의 이긴 판을 먼저 고른다
        g = r["groups"].get("pro") or {}
        lo, hi = sorted([g.get("median", 0), g.get("p75" if r["higher_better"] else "p25", 0)])
        cand = sorted((x for x in rows if x.get(key) is not None),
                      key=lambda x: (not (lo <= x[key] <= hi), not x["win"], abs(x[key] - g.get("median", 0))))
        picked, players = [], set()
        for x in cand:
            who = names.get(x["puuid"], "프로")
            if who in players:
                continue
            players.add(who)
            t = WATCH_AT.get(key)
            t = max(0, x[key] - 20) if t is None else t
            picked.append({"match_id": x["match_id"], "player": who, "champion_id": x["champion_id"],
                           "value": x[key], "t": t, "win": x["win"]})
            if len(picked) >= per:
                break
        out[key] = picked
    return out


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
                f["match_id"], f["puuid"] = mid, pu
                rows.append(f)
        groups.setdefault(name, []).extend(rows)
        print(name, len(rows), flush=True)
    high = tuple(g for g in ("pro", "challenger", "apex") if g in groups)
    ref = build_reference(groups, high, "platinum")
    names = {}
    acc = Path(__file__).resolve().parents[2] / "research_notes" / "검증" / "pro_accounts.json"
    if acc.exists():
        names = {a["puuid"]: a["player"] for a in json.loads(acc.read_text()) if a.get("puuid")}
    if "pro" in groups:
        ref["exemplars"] = exemplars(groups["pro"], ref, names)
    out.write_text(json.dumps(ref, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in sorted(ref["features"].items(), key=lambda kv: -kv[1]["auc"]):
        g = v["groups"]
        print(f"{k:15} auc {v['auc']:.2f} (win {v['auc_win']}, loss {v['auc_loss']}) {'✅' if v['validated'] else '  '} "
              + " ".join(f"{n}={x['median']}" for n, x in g.items()))


main()
