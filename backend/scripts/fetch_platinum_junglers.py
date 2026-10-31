"""검증용: 플래티넘 정글러 N명의 최근 정글 경기를 받아 저장한다."""
import asyncio
import json
import sys
from pathlib import Path

from loldosa.config import load_settings
from loldosa.riot.client import RiotClient
from loldosa.store.matches import MatchStore

OUT = Path(sys.argv[1])
N_PLAYERS, GAMES = int(sys.argv[2]), int(sys.argv[3])


async def main():
    s = load_settings()
    store = MatchStore(OUT, filename="validation.duckdb")
    picked = {}
    async with RiotClient(s.riot_api_key, s.platform, s.region) as riot:
        entries = []
        for div in ("I", "II", "III", "IV"):
            entries += await riot.league_entries("PLATINUM", div, 1)
        for e in entries:
            if len(picked) >= N_PLAYERS:
                break
            ids = await riot.match_ids(e["puuid"], count=15)
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
    (OUT / "platinum_players.json").write_text(json.dumps(picked))

asyncio.run(main())
