"""Riot API 키 없이 내 경기 가져오기: 롤 클라이언트(LCU)의 전적 API → Match-V5 모양으로 바꾼다.

LCU 는 로그인한 내 계정의 최근 경기와 타임라인을 키 없이 준다 (구형 v4 모양).
  /lol-match-history/v1/products/lol/current-summoner/matches?begIndex=0&endIndex=20
  /lol-match-history/v1/games/{gameId}
  /lol-match-history/v1/game-timelines/{gameId}
Match-V5 에만 있는 값(challenges, 핑 횟수, teamPosition)은 없거나 다르게 들어 있어서,
- 포지션: 강타(11)를 들었으면 정글, 아니면 timeline.lane/role 로 추정
- challenges·핑: 없음 → 챌린저 갭에서 그 지표는 '측정 안 됨'으로 빠진다
실제 응답 모양은 진단 기록(lcu_matchhistory_*.jsonl)에 남겨 두고 맞춰 간다.
"""

from __future__ import annotations

SMITE = 11
LANE = {"TOP": "TOP", "JUNGLE": "JUNGLE", "MIDDLE": "MIDDLE", "MID": "MIDDLE"}


def _position(p: dict) -> str:
    if SMITE in (p.get("spell1Id"), p.get("spell2Id")):
        return "JUNGLE"
    tl = p.get("timeline") or {}
    lane, role = (tl.get("lane") or "").upper(), (tl.get("role") or "").upper()
    if lane in LANE:
        return LANE[lane]
    if lane in ("BOTTOM", "BOT"):
        return "UTILITY" if "SUPPORT" in role else "BOTTOM"
    return ""


def to_v5(game: dict, timeline: dict | None, platform: str = "KR") -> tuple[dict, dict]:
    """LCU 경기·타임라인 → (Match-V5 match, Match-V5 timeline)."""
    ids = {pi["participantId"]: (pi.get("player") or {}) for pi in game.get("participantIdentities", [])}
    teams_win = {t.get("teamId"): str(t.get("win", "")).lower() in ("win", "true") for t in game.get("teams", [])}
    parts = []
    for p in game.get("participants", []):
        st = p.get("stats") or {}
        pl = ids.get(p["participantId"], {})
        win = st.get("win")
        parts.append({
            **st,  # 이름이 같은 값(kills, deaths, visionScore, goldEarned, wardsPlaced ...)은 그대로
            "participantId": p["participantId"], "teamId": p["teamId"], "championId": p["championId"],
            "puuid": pl.get("puuid", ""), "riotIdGameName": pl.get("gameName") or pl.get("summonerName", ""),
            "riotIdTagline": pl.get("tagLine", ""),
            "win": bool(win) if win is not None else teams_win.get(p["teamId"], False),
            "teamPosition": _position(p), "summoner1Id": p.get("spell1Id"), "summoner2Id": p.get("spell2Id"),
            "challenges": {},
        })
    dur = game.get("gameDuration", 0)
    if dur > 100_000:  # 일부 응답은 ms
        dur //= 1000
    gid = game.get("gameId")
    mid = f"{platform.upper()}_{gid}"
    match = {"metadata": {"matchId": mid, "participants": [x["puuid"] for x in parts]},
             "info": {"gameId": gid, "gameDuration": dur, "gameStartTimestamp": game.get("gameCreation", 0),
                      "gameVersion": game.get("gameVersion", ""), "queueId": game.get("queueId", 0),
                      "participants": parts,
                      "teams": [{"teamId": t.get("teamId"), "win": teams_win.get(t.get("teamId"), False),
                                 "bans": t.get("bans", [])} for t in game.get("teams", [])]}}
    frames = []
    for fr in (timeline or {}).get("frames", []):
        pfs = {}
        for k, pf in (fr.get("participantFrames") or {}).items():
            pfs[str(k)] = {**pf, "participantId": pf.get("participantId", int(k))}
        evs = []
        for e in fr.get("events", []):
            e = dict(e)
            e["type"] = e.get("type", "")
            evs.append(e)
        frames.append({"timestamp": fr.get("timestamp", 0), "participantFrames": pfs, "events": evs})
    tl = {"metadata": {"matchId": mid}, "info": {"frameInterval": 60000, "frames": frames}}
    return match, tl


async def recent_game_ids(lcu, count: int = 20, queues: set[int] | None = None) -> list[int]:
    """최근 경기 id. 기본은 협곡 5:5 전부 (일반·솔랭·자랭·빠른 대전)."""
    from ..review.sync import SR_QUEUES

    queues = SR_QUEUES if queues is None else queues
    data = await lcu.get(f"/lol-match-history/v1/products/lol/current-summoner/matches?begIndex=0&endIndex={count}")
    games = ((data or {}).get("games") or {}).get("games", [])
    return [g["gameId"] for g in games if not queues or g.get("queueId") in queues]


async def fetch(lcu, game_id: int, platform: str = "KR", diag_dir=None) -> tuple[dict, dict] | None:
    game = await lcu.get(f"/lol-match-history/v1/games/{game_id}")
    if not game or not game.get("participants"):
        return None
    timeline = await lcu.get(f"/lol-match-history/v1/game-timelines/{game_id}")
    if diag_dir:  # 실제 응답 모양을 남겨서 변환을 맞춰 간다 (개인정보: 닉네임 정도만 들어 있음)
        from .postgame import diag_write
        diag_write(diag_dir, "lcu_matchhistory", {"game": game, "timeline_frames": len((timeline or {}).get("frames", [])),
                                                  "timeline_sample": ((timeline or {}).get("frames") or [None])[:2]})
    return to_v5(game, timeline, platform)
