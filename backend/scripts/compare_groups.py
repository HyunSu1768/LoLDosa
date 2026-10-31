"""validate_study.py 결과(raw)로 그룹별 측정값 평균·첫 드래곤 전 귀환 분포를 비교한다. 사용: python scripts/compare_groups.py <result.json>..."""
import json, statistics as st, sys
groups = {}
for f in sys.argv[1:]:
    groups.update(json.load(open(f)))
def mean(xs):
    xs = [x for x in xs if x is not None]
    return (round(st.mean(xs), 2), len(xs)) if xs else (None, 0)
keys = ["camps3", "cs10", "deaths10", "risky_deaths10", "enemy_ganks10", "far_lost", "traded", "vision_pm", "first_recall_s"]
for k in keys:
    print(f"{k:16}", "  ".join(f"{g}={mean([r[k] for r in v['raw']])[0]}" for g, v in groups.items()))
print("gold_death>0     ", "  ".join(f"{g}={mean([1 if r['gold_death'] else 0 for r in v['raw']])[0]}" for g, v in groups.items()))
print("bad_band_fight   ", "  ".join(f"{g}={mean([1 if r['bad_band_fight'] else 0 for r in v['raw']])[0]}" for g, v in groups.items()))
for g, v in groups.items():
    d = {}
    for r in v["raw"]:
        if r["dragon_turn"]:
            d.setdefault(r["dragon_turn"], [0, 0]); d[r["dragon_turn"]][0] += 1; d[r["dragon_turn"]][1] += bool(r["dragon_took"])
    n = sum(x[0] for x in d.values())
    print(g, "dragon turn:", {k: f"{x[0]/n:.0%} (take {x[1]}/{x[0]})" for k, x in d.items()}, "n", n, "winrate", mean([1 if r['win'] else 0 for r in v['raw']])[0])
