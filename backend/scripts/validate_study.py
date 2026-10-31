"""검증 연구: 그룹(챌린저·프로·플래티넘)별로 LoLDosa 분석을 돌려 비교한다.

분석이 맞다면 고수 그룹이
- 목표 체크를 더 자주 통과하고
- 판단 훈련에서 실제 선택이 '비슷한 상황 고티어의 20% 이상이 고른 행동'에 더 자주 들어가야 한다.
고티어 통계(정답지)는 검증 대상 경기를 뺀 홀드아웃으로 만든다.

사용: python scripts/validate_study.py <holdout_stats_dir> <out.json> <group>=<store.duckdb>:<players.json> ...
players.json: {puuid: [match_id, ...]}
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

from loldosa.analysis.query import StatsDB
from loldosa.ddragon import load_cached
from loldosa.review.analyze import Reviewer
from loldosa.review.moments import build_moments
from loldosa.store.matches import MatchStore


def run_group(store_path: Path, players: dict, stats: StatsDB, champs) -> dict:
    store = MatchStore(store_path.parent, filename=store_path.name)
    checks = defaultdict(lambda: [0, 0])
    moments = {"n": 0, "agree": 0, "top1": 0, "by_reason": defaultdict(lambda: [0, 0])}
    games = 0
    raw = []  # 게임별 측정값: 통과/실패 기준을 바꾸기 전에 분포 자체를 비교하려고 남긴다
    for puuid, mids in players.items():
        for mid in mids:
            try:
                rv = Reviewer(store, stats, champs).review(mid, puuid)
            except KeyError:
                continue
            if not rv.is_jungle:
                continue
            games += 1
            f = rv.facts
            raw.append({k: f.get(k) for k in ("camps3", "cs10", "cs10_bench", "deaths10", "risky_deaths10", "enemy_ganks10",
                                              "far_lost", "traded", "gold_death", "vision_pm", "first_recall_s", "bad_band_fight")}
                       | {"dragon_turn": (f.get("obj_turns") or {}).get("DRAGON", {}).get("turn"),
                          "dragon_took": (f.get("obj_turns") or {}).get("DRAGON", {}).get("took"),
                          "win": rv.summary.get("win")})
            for c in rv.checks:
                if c["status"] != "na":
                    checks[c["concept"]][1] += 1
                    checks[c["concept"]][0] += c["status"] == "pass"
            with stats.session():
                for mo in build_moments(store.con, stats, champs, mid, puuid):
                    moments["n"] += 1
                    ok = mo["mine"]["action"] in mo["good"]
                    moments["agree"] += ok
                    moments["top1"] += bool(mo["crowd"]) and mo["crowd"][0]["action"] == mo["mine"]["action"]
                    key = mo["reason"].split(" ", 1)[-1] if "죽기" not in mo["reason"] else "죽기 30초 전"
                    for k in ("죽기 30초 전", "상대 정글 갱 직전", "1분 전", "3:00"):
                        if k in mo["reason"]:
                            key = k
                    moments["by_reason"][key][1] += 1
                    moments["by_reason"][key][0] += ok
    store.close()
    return {"players": len(players), "games": games, "raw": raw,
            "checks": {k: {"pass": v[0], "total": v[1], "rate": round(v[0] / v[1], 3) if v[1] else None} for k, v in checks.items()},
            "moments": {"n": moments["n"], "agree_rate": round(moments["agree"] / moments["n"], 3) if moments["n"] else None,
                        "top1_rate": round(moments["top1"] / moments["n"], 3) if moments["n"] else None,
                        "by_reason": {k: {"agree": v[0], "n": v[1]} for k, v in moments["by_reason"].items()}}}


def main():
    stats_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
    stats = StatsDB(stats_dir / "stats.duckdb")
    champs = load_cached(stats_dir)
    result = {}
    for arg in sys.argv[3:]:
        name, rest = arg.split("=", 1)
        store_path, players_path = rest.split(":", 1)
        players = json.loads(Path(players_path).read_text())
        result[name] = run_group(Path(store_path), players, stats, champs)
        print(name, result[name]["games"], "games", json.dumps(result[name]["moments"], ensure_ascii=False)[:200], flush=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
