"""챔피언 성향(조합 유형 점수)을 실제 경기 기록으로 계산해 learn/champ_traits.json 에 저장한다.

손으로 '이 챔피언은 돌진형' 같은 꼬리표를 붙이지 않고, 그 챔피언이 실제 경기에서 한 일로 잰다.
- engage  (돌진·한타 열기): 상대를 묶은 횟수·묶은 시간(분당) + 팀 안에서 맞아 준 비중
- poke    (포킹): 받은 피해 대비 준 피해 + 맞힌 스킬샷(분당)
- pick    (끊기): 아군과 같이 끊은 킬, 묶고 같이 잡은 킬(분당)
- protect (지키기): 아군에게 준 회복·보호막(분당), 라이엇 서포터 태그가 있는 챔피언만 핵심으로 셈
- split   (사이드): 후반 혼자 민 포탑, 솔로킬, 건물 피해(분당)
- siege   (공성): 건물 피해(분당) + 포킹
- late    (후반 힘): 30분 이후 승률 − 25분 전 승률 (표본 수로 줄여 잡음)
점수는 챔피언끼리 비교한 백분위(0~1)라서 0.5 가 평균 챔피언이다.

사용: python scripts/build_champ_traits.py ../data
"""

from __future__ import annotations

import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "src/loldosa/learn/champ_traits.json"
MIN_GAMES = 15


def pct_rank(values: dict[int, float]) -> dict[int, float]:
    order = sorted(values, key=lambda k: values[k])
    n = len(order)
    return {k: (i / (n - 1) if n > 1 else 0.5) for i, k in enumerate(order)}


def main(data_dir: str) -> None:
    raw = sorted(Path(data_dir, "raw").glob("*.json.gz"))
    acc: dict[int, dict] = defaultdict(lambda: defaultdict(float))
    patches = set()
    for f in raw:
        try:
            m = json.load(gzip.open(f))["match"]["info"]
        except Exception:  # noqa: BLE001
            continue
        if m.get("queueId") not in (420, 440) or m["gameDuration"] < 900:
            continue
        patches.add(".".join(m["gameVersion"].split(".")[:2]))
        mins = m["gameDuration"] / 60
        team_tank = defaultdict(float)
        for p in m["participants"]:
            team_tank[p["teamId"]] += p["totalDamageTaken"] + p["damageSelfMitigated"]
        for p in m["participants"]:
            c, ch = p["championId"], p.get("challenges", {})
            a = acc[c]
            a["games"] += 1
            a["immob"] += ch.get("enemyChampionImmobilizations", 0) / mins
            a["ccdealt"] += p["totalTimeCCDealt"] / mins  # 말파이트처럼 한 번에 여럿을 오래 묶는 챔피언
            a["tank"] += (p["totalDamageTaken"] + p["damageSelfMitigated"]) / max(team_tank[p["teamId"]], 1)
            a["ratio"] += p["totalDamageDealtToChampions"] / max(p["totalDamageTaken"], 1)
            a["skill"] += ch.get("skillshotsHit", 0) / mins
            a["pick"] += (ch.get("pickKillWithAlly", 0) + ch.get("immobilizeAndKillWithAlly", 0)) / mins
            a["heal"] += (p["totalHealsOnTeammates"] + p["totalDamageShieldedOnTeammates"]) / mins
            a["solo_t"] += ch.get("soloTurretsLategame", 0)
            a["solo_k"] += ch.get("soloKills", 0)
            a["bld"] += p["damageDealtToBuildings"] / mins
            if m["gameDuration"] < 25 * 60:
                a["e_g"] += 1; a["e_w"] += p["win"]
            elif m["gameDuration"] >= 30 * 60:
                a["l_g"] += 1; a["l_w"] += p["win"]
    champs = {c: a for c, a in acc.items() if a["games"] >= MIN_GAMES}
    tags = {}
    for f in Path(data_dir, "ddragon").glob("*/champion.*.json"):
        tags = {int(v["key"]): tuple(v.get("tags", ())) for v in json.loads(f.read_text(encoding="utf-8"))["data"].values()}
    avg = lambda k: {c: a[k] / a["games"] for c, a in champs.items()}  # noqa: E731
    P = {k: pct_rank(avg(k)) for k in ("immob", "ccdealt", "tank", "ratio", "skill", "pick", "heal", "solo_t", "solo_k", "bld")}

    def shrink(w, g, k=20):
        return (w + 0.5 * k) / (g + k)

    late = {c: shrink(a["l_w"], a["l_g"]) - shrink(a["e_w"], a["e_g"]) for c, a in champs.items()}
    PL = pct_rank(late)
    out = {}
    for c, a in champs.items():
        poke = 0.5 * P["ratio"][c] + 0.5 * P["skill"][c]
        out[str(c)] = {
            "games": int(a["games"]),
            "support": "Support" in tags.get(c, ()),  # 아군 회복 기록에 자기 회복이 섞이는 챔피언(피오라 등)이 있어서 '지키기'는 서포터 태그와 같이 본다
            "engage": round(0.35 * P["immob"][c] + 0.35 * P["ccdealt"][c] + 0.3 * P["tank"][c], 3),
            "poke": round(poke, 3),
            "pick": round(P["pick"][c], 3),
            "protect": round(P["heal"][c], 3),
            "split": round(0.6 * P["solo_t"][c] + 0.2 * P["solo_k"][c] + 0.2 * P["bld"][c], 3),
            "siege": round(0.5 * P["bld"][c] + 0.5 * poke, 3),
            "tank": round(P["tank"][c], 3),
            "late": round(PL[c], 3),
            "late_diff": round(late[c], 4),
        }
    OUT.write_text(json.dumps({"patches": sorted(patches), "games": len(raw), "min_games": MIN_GAMES, "champions": out},
                              ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(out)} champions from {len(raw)} games → {OUT}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../data")
