"""검증용: 한 티어 정글러 N명의 최근 정글 경기를 받아 저장한다.

사용: python scripts/fetch_platinum_junglers.py <outdir> <n_players> <games> [TIER] [page]
출력: <outdir>/validation_<tier>.duckdb (PLATINUM 기본은 validation.duckdb), <outdir>/<tier>_players.json
"""
import asyncio
import json
import sys
from pathlib import Path

from loldosa.config import load_settings
from loldosa.riot.client import RiotClient
from loldosa.store.matches import MatchStore

OUT = Path(sys.argv[1])
N_PLAYERS, GAMES = int(sys.argv[2]), int(sys.argv[3])
TIER = sys.argv[4] if len(sys.argv) > 4 else "PLATINUM"
PAGE = int(sys.argv[5]) if len(sys.argv) > 5 else 1
# 6번째 인자: 이 날짜(유닉스 초) 이후 경기만 (최근 패치 표본을 모을 때). 예: 3패치 ≈ 42일 전
START = int(sys.argv[6]) if len(sys.argv) > 6 else None


async def main():
    s = load_settings()
    store = MatchStore(OUT, filename="validation.duckdb" if TIER == "PLATINUM" and PAGE == 1 else f"validation_{TIER.lower()}_{PAGE}.duckdb")
    picked = {}
    async with RiotClient(s.riot_api_key, s.platform, s.region) as riot:
        entries = []
        for div in ("I", "II", "III", "IV"):
            entries += await riot.league_entries(TIER, div, PAGE)
        for e in entries:
            if len(picked) >= N_PLAYERS:
                break
            ids = await riot.match_ids(e["puuid"], count=15, start_time=START)
            jungle = []
            for mid in ids:
                if len(jungle) >= GAMES:
                    break
                m = await riot.match(mid)
                if not m or m["info"]["gameDuration"] < 900:
                    continue
                me = next(p for p in m["info"]["participants"] if p["puuid"] == e["puuid"])
                if me.get("teamPosition") != "JUNGLE":
                    if not jungle and len([x for x in ids[:4]]) and mid == ids[3]:
                        break  # 최근 4판에 정글이 없으면 정글러가 아님
                    continue
                tl = await riot.timeline(mid)
                if tl:
                    store.save_raw(mid, m, tl)
                    store.ingest(m, tl, "validation")
                    jungle.append(mid)
            if len(jungle) >= 3:
                picked[e["puuid"]] = {"tier": e["tier"], "rank": e["rank"], "lp": e["leaguePoints"], "matches": jungle}
                print(len(picked), e["tier"], e["rank"], len(jungle), flush=True)
    store.close()
    name = "platinum_players.json" if TIER == "PLATINUM" and PAGE == 1 else f"{TIER.lower()}_{PAGE}_players.json"
    (OUT / name).write_text(json.dumps(picked))

asyncio.run(main())
