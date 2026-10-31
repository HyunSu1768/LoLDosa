"""검증용: research_notes/검증/pro_accounts.json 의 확인된 프로 정글러 계정에서 최근 정글 솔랭을 받아 저장한다.

사용: python scripts/fetch_pro_junglers.py <pro_accounts.json> <outdir> <games_per_player>
출력: <outdir>/pro.duckdb, <outdir>/pro_players.json ({puuid: [match_id, ...]})
"""
import asyncio
import json
import sys
from pathlib import Path

from loldosa.config import load_settings
from loldosa.riot.client import RiotClient
from loldosa.store.matches import MatchStore


async def main():
    accounts = [a for a in json.loads(Path(sys.argv[1]).read_text()) if a.get("verified") and a.get("puuid")]
    out, games = Path(sys.argv[2]), int(sys.argv[3])
    s = load_settings()
    store = MatchStore(out, filename="pro.duckdb")
    picked = {}
    async with RiotClient(s.riot_api_key, s.platform, s.region) as riot:
        for a in accounts:
            ids = await riot.match_ids(a["puuid"], count=25)
            jungle = []
            for mid in ids:
                if len(jungle) >= games:
                    break
                m = await riot.match(mid)
                if not m or m["info"].get("queueId") != 420 or m["info"]["gameDuration"] < 900:
                    continue
                me = next(p for p in m["info"]["participants"] if p["puuid"] == a["puuid"])
                if me.get("teamPosition") != "JUNGLE":
                    continue
                tl = await riot.timeline(mid)
                if tl:
                    store.save_raw(mid, m, tl)
                    store.ingest(m, tl, "pro")
                    jungle.append(mid)
            if jungle:
                picked[a["puuid"]] = jungle
            print(a["player"], len(jungle), flush=True)
    store.close()
    (out / "pro_players.json").write_text(json.dumps(picked))

asyncio.run(main())
