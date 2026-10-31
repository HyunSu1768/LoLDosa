"""게임 종료 감지: LCU gameflow 를 보고 있다가 솔랭이 끝나면 gameId 를 알려준다.

InProgress 동안 /lol-gameflow/v1/session 에서 gameId·큐를 기억해 두고,
InProgress → (WaitingForStats | PreEndOfGame | EndOfGame | 그 밖의 단계) 로 넘어가면 한 번 이벤트를 낸다.
게임 도중 클라이언트를 껐다 켜도(재접속) 같은 gameId 는 한 번만 알린다.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from .client import LcuClient
from .connection import find_credentials

log = logging.getLogger(__name__)

IN_GAME = {"InProgress", "Reconnect"}
SOLO_QUEUES = {400, 420, 430, 440, 490}  # 협곡 5:5 전부 (일반 게임도 자동 복기)


@dataclass
class GameEndDetector:
    queues: set[int] = field(default_factory=lambda: set(SOLO_QUEUES))
    phase: str = "None"
    current: dict | None = None
    announced: set[int] = field(default_factory=set)

    def feed(self, phase: str, session: dict | None) -> dict | None:
        """단계 하나를 넣으면, 막 끝난 게임이 있을 때 {"game_id", "queue_id"} 를 돌려준다."""
        prev, self.phase = self.phase, phase
        if phase in IN_GAME:
            gd = (session or {}).get("gameData") or {}
            gid = gd.get("gameId")
            if gid:
                self.current = {"game_id": int(gid), "queue_id": (gd.get("queue") or {}).get("id")}
            return None
        if prev in IN_GAME and self.current:
            ev, self.current = self.current, None
            if ev["game_id"] in self.announced or (self.queues and ev["queue_id"] not in self.queues):
                return None
            self.announced.add(ev["game_id"])
            return ev
        return None


async def watch_game_end(interval: float = 3.0, log_dir: Path | None = None) -> AsyncIterator[dict]:
    """솔랭이 시작되면 {"type": "start"}, 끝나면 {"type": "end"} 를 yield. log_dir 가 있으면 단계 변화를 진단 기록으로."""
    det = GameEndDetector()
    client: LcuClient | None = None
    last_phase = None
    try:
        while True:
            if client is None:
                creds = find_credentials()
                if creds is None:
                    await asyncio.sleep(5.0)
                    continue
                client = LcuClient(creds)
            try:
                phase = await client.gameflow_phase()
                session = await client.get("/lol-gameflow/v1/session") if phase in IN_GAME else None
            except (httpx.TransportError, httpx.HTTPStatusError) as e:
                log.info("LCU 연결 끊김 (%s)", e)
                await client.aclose()
                client = None
                await asyncio.sleep(5.0)
                continue
            if phase != last_phase:
                last_phase = phase
                if log_dir:
                    diag_write(log_dir, "gameflow", {"phase": phase,
                                                    "game_id": ((session or {}).get("gameData") or {}).get("gameId")})
            before = (det.current or {}).get("game_id")
            ev = det.feed(phase, session)
            now = det.current
            if now and now["game_id"] != before and (not det.queues or now["queue_id"] in det.queues):
                yield {"type": "start", **now}
            if ev:
                yield {"type": "end", **ev}
            await asyncio.sleep(interval)
    finally:
        if client is not None:
            await client.aclose()


def diag_write(log_dir: Path, kind: str, payload) -> None:
    """진단 기록: 실제 클라이언트에서 무슨 응답이 왔는지 남겨서, 문제가 생기면 파일 하나로 공유할 수 있게."""
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        day = time.strftime("%Y%m%d")
        with (log_dir / f"{kind}_{day}.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "data": payload}, ensure_ascii=False) + "\n")
    except OSError:
        log.warning("진단 기록 실패", exc_info=True)
