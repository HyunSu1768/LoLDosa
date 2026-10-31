"""녹화된 챔선 세션(JSONL)을 재생. 게임 없이 브리핑 흐름을 테스트할 때 쓴다.

한 줄 = LCU /lol-champ-select/v1/session 응답 하나 (null 이면 챔선 종료).
`loldosa lcu watch --record 파일` 로 실제 챔선을 녹화할 수 있다.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from pathlib import Path

from .champselect import ChampSelectState, parse_session


def load_sessions(path: Path) -> list[dict | None]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


async def replay(path: Path, interval: float = 1.0) -> AsyncIterator[ChampSelectState | None]:
    last_sig = None
    for session in load_sessions(path):
        if session is None:
            if last_sig is not None:
                last_sig = None
                yield None
        else:
            state = parse_session(session)
            if (sig := state.signature()) != last_sig:
                last_sig = sig
                yield state
        await asyncio.sleep(interval)
