"""테스트용: Match-V5 경기를 롤 클라이언트 전적 API(구형 v4) 모양으로 되돌린다."""


def v5_to_lcu(match: dict, timeline: dict) -> tuple[dict, dict]:
    info = match["info"]
    parts, idents = [], []
    for p in info["participants"]:
        st = {k: v for k, v in p.items() if k not in ("participantId", "teamId", "championId", "puuid", "teamPosition",
                                                       "challenges", "summoner1Id", "summoner2Id")}
        lane = {"JUNGLE": "JUNGLE", "TOP": "TOP", "MIDDLE": "MIDDLE", "BOTTOM": "BOTTOM", "UTILITY": "BOTTOM"}.get(p.get("teamPosition"), "NONE")
        parts.append({"participantId": p["participantId"], "teamId": p["teamId"], "championId": p["championId"],
                      "spell1Id": p.get("summoner1Id"), "spell2Id": p.get("summoner2Id"), "stats": st,
                      "timeline": {"lane": lane, "role": "DUO_SUPPORT" if p.get("teamPosition") == "UTILITY" else "SOLO"}})
        idents.append({"participantId": p["participantId"], "player": {"puuid": p["puuid"], "gameName": p.get("riotIdGameName", ""),
                                                                       "tagLine": p.get("riotIdTagline", "")}})
    game = {"gameId": info["gameId"], "gameCreation": info["gameStartTimestamp"], "gameDuration": info["gameDuration"],
            "gameVersion": info["gameVersion"], "queueId": info["queueId"], "participants": parts,
            "participantIdentities": idents,
            "teams": [{"teamId": t["teamId"], "win": "Win" if t["win"] else "Fail", "bans": t.get("bans", [])} for t in info["teams"]]}
    return game, {"frames": timeline["info"]["frames"]}
