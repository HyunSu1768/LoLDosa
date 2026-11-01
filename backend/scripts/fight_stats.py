"""한타 통계 (KR 솔랭 타임라인): 킬이 20초 안에 이어진 3킬 이상 묶음을 '한타'로 보고,
- 첫 킬을 낸 팀이 그 한타를 이긴(킬을 더 많이 낸) 비율
- 한타 직전 1분 팀 골드 차별 승률
- 오브젝트(드래곤·유충·전령·바론) 처치 60초 전~10초 후 사이 한타를 이긴 팀이 그 오브젝트를 가져간 비율
을 센다. 사용: python scripts/fight_stats.py ../data/matches.duckdb"""
import sys
from collections import defaultdict

import duckdb

con = duckdb.connect(sys.argv[1], read_only=True)
teams = {(m, p): t for m, p, t in con.execute("select match_id, participant_id, team_id from participants").fetchall()}
gold = defaultdict(dict)
for m, p, mi, g in con.execute("select match_id, participant_id, minute, total_gold from frames").fetchall():
    gold[(m, mi)][p] = g
ev = defaultdict(list)
for m, ts, ty, k, v, mt, tid in con.execute(
        "select match_id, ts_ms, type, participant_id, victim_id, monster_type, team_id from events "
        "where type in ('CHAMPION_KILL','ELITE_MONSTER_KILL') order by match_id, ts_ms").fetchall():
    ev[m].append((ts, ty, k, v, mt, tid))
fights, first_win, gold_bins, obj = 0, 0, defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
size_first = defaultdict(lambda: [0, 0])
for m, es in ev.items():
    kills = [e for e in es if e[1] == "CHAMPION_KILL" and e[3]]
    groups, cur = [], []
    for e in kills:
        if cur and e[0] - cur[-1][0] > 20000:
            groups.append(cur); cur = []
        cur.append(e)
    if cur: groups.append(cur)
    for g in groups:
        if len(g) < 3:
            continue
        side = lambda e: 300 - teams.get((m, e[3]), 100)  # 킬한 팀 = 죽은 사람 반대 팀
        cnt = defaultdict(int)
        for e in g: cnt[side(e)] += 1
        if cnt[100] == cnt[200]:
            continue
        win = 100 if cnt[100] > cnt[200] else 200
        fights += 1
        f = side(g[0]) == win
        first_win += f
        b = min(len(g), 6)
        size_first[b][0] += f; size_first[b][1] += 1
        mi = max(0, int(g[0][0] // 60000) - 1)
        gg = gold.get((m, mi), {})
        diff = sum(v for p, v in gg.items() if teams.get((m, p)) == 100) - sum(v for p, v in gg.items() if teams.get((m, p)) == 200)
        lead = diff if win == 100 else -diff  # 이긴 팀 기준 골드 차
        # 골드 차 구간별: 앞선 팀이 이긴 비율
        bucket = min(abs(diff) // 1000, 5)
        gold_bins[bucket][0] += (diff > 0) == (win == 100)
        gold_bins[bucket][1] += 1
        for e in es:
            if e[1] == "ELITE_MONSTER_KILL" and g[0][0] - 10000 <= e[0] <= g[-1][0] + 60000 and e[4] in ("DRAGON", "HORDE", "RIFTHERALD", "BARON_NASHOR"):
                obj[e[4]][0] += e[5] == win; obj[e[4]][1] += 1
                break
print(f"한타(20초 안 3킬 이상) {fights:,}개")
print(f"첫 킬을 낸 팀이 한타를 이긴 비율: {first_win / fights:.1%}")
for b, (w, n) in sorted(size_first.items()): print(f"  킬 {b}{'+' if b == 6 else ''}개 한타: 첫 킬 팀 승 {w / n:.1%} (n={n:,})")
for b, (w, n) in sorted(gold_bins.items()): print(f"  직전 골드 차 {b}k~{b + 1}k{'+' if b == 5 else ''}: 앞선 팀 승 {w / n:.1%} (n={n:,})")
for k, (w, n) in obj.items(): print(f"  {k} 근처 한타 이긴 팀이 그 오브젝트 획득: {w / n:.1%} (n={n:,})")
