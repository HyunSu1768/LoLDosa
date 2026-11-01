"""브리핑 플랜이 판마다 얼마나 똑같은지 재기.

실제 경기 N판의 10명 조합으로 챔피언 선택 '최종' 상태를 만들고(블루팀 정글 = 나), 브리핑을 만들어
- 플랜 줄(이번 판 플랜 + 전체 운영 헤드라인·세부)마다 서로 다른 문장 비율
- 판마다 '이 판에만 나온 구체 정보'(챔피언 이름·숫자가 들어간 줄) 개수
를 센다. 모든 판에 똑같이 나오는 줄 = 쓸모없는 줄.

사용: python scripts/plan_diversity.py ../data/matches.duckdb ../data/stats.duckdb 120
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import duckdb

from loldosa.analysis.query import StatsDB
from loldosa.briefing.engine import BriefingEngine
from loldosa.config import load_settings
from loldosa.ddragon import load_cached
from loldosa.lcu.champselect import ChampSelectState, Slot, Stage

POS = {"TOP": "top", "JUNGLE": "jungle", "MIDDLE": "middle", "BOTTOM": "bottom", "UTILITY": "utility"}


def states(matches_db: str, n: int):
    con = duckdb.connect(matches_db, read_only=True)
    ids = [r[0] for r in con.execute(
        "SELECT match_id FROM participants GROUP BY 1 HAVING count(DISTINCT position)=5 ORDER BY hash(match_id) LIMIT ?", [n]).fetchall()]
    for mid in ids:
        rows = con.execute("SELECT participant_id, team_id, position, champion_id FROM participants WHERE match_id=? ORDER BY participant_id",
                           [mid]).fetchall()
        allies, enemies, me = [], [], None
        for pid, team, pos, champ in rows:
            s = Slot(pid, POS.get(pos, "") if team == 100 else "", champ, 0, True, (0, 0), team)
            (allies if team == 100 else enemies).append(s)
            if team == 100 and pos == "JUNGLE":
                me = pid
        if me:
            yield mid, ChampSelectState(Stage.FINAL, "FINALIZATION", me, tuple(allies), tuple(enemies), (), ())


def main(matches_db: str, stats_db: str, n: int) -> None:
    s = load_settings()
    eng = BriefingEngine(StatsDB(Path(stats_db)), load_cached(s.data_dir, s.locale), s.data_dir / "guides.duckdb")
    lines: dict[str, Counter] = {}
    specific = []
    games = 0
    for mid, st in states(matches_db, n):
        b = eng.build(st)
        games += 1
        got = [(f"plan:{p.title}", p.text) for p in b.plan]
        for ph in (b.game_plan or {}).get("phases", []):
            got.append((f"phase:{ph['key']}:headline", ph["headline"]))
            got += [(f"phase:{ph['key']}:item", i["text"]) for i in ph["items"] if i["kind"] != "rule"]
            got += [(f"phase:{ph['key']}:why", i["why"]) for i in ph["items"] if i["kind"] != "rule" and i.get("why")]
        if b.game_plan.get("vs"):
            got.append(("vs", b.game_plan["vs"]))
        k = 0
        for slot, text in got:
            lines.setdefault(slot, Counter())[text] += 1
            names = [c for c in (eng.name(x.champion_id) for x in st.allies + st.enemies) if c and c in text]
            k += bool(names or re.search(r"\d", text))
        specific.append(k)
    print(f"{games}판")
    print(f"{'자리':28} {'나온 판':>6} {'서로 다른 문장':>12} {'가장 흔한 문장 비율':>16}")
    tot = same = 0
    for slot, c in sorted(lines.items()):
        n_slot = sum(c.values())
        top = c.most_common(1)[0]
        tot += n_slot
        same += top[1]
        print(f"{slot:28} {n_slot:6} {len(c):12} {top[1] / n_slot:15.0%}   e.g. {top[0][:60]}")
    print(f"\n전체 줄 중 '그 자리에서 가장 흔한 문장'과 똑같은 비율: {same / tot:.0%}")
    print(f"판마다 챔피언 이름·숫자가 든 구체적인 줄: 평균 {sum(specific) / len(specific):.1f}개")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 120)
