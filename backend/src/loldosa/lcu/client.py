"""LCU HTTP 클라이언트 + 챔피언 선택 감시 루프."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator

import httpx

from .champselect import ChampSelectState, parse_session
from .connection import LcuCredentials, find_credentials

log = logging.getLogger(__name__)


class LcuClient:
    def __init__(self, creds: LcuCredentials, transport: httpx.AsyncBaseTransport | None = None) -> None:
        # LCU 는 Riot 자체 서명 인증서를 쓰는 127.0.0.1 전용 서버라 검증을 끈다.
        self._http = httpx.AsyncClient(
            base_url=creds.base_url,
            auth=("riot", creds.password),
            verify=False,
            timeout=5.0,
            transport=transport,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def get(self, path: str) -> dict | list | str | None:
        resp = await self._http.get(path)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def gameflow_phase(self) -> str:
        return await self.get("/lol-gameflow/v1/gameflow-phase") or "None"

    async def champ_select_session(self) -> dict | None:
        return await self.get("/lol-champ-select/v1/session")

    async def current_summoner(self) -> dict | None:
        return await self.get("/lol-summoner/v1/current-summoner")


async def watch_champ_select(interval: float = 1.0) -> AsyncIterator[ChampSelectState | None]:
    """챔피언 선택 상태가 의미 있게 바뀔 때마다 yield. 챔선이 끝나면 None 을 한 번 yield.

    클라이언트가 꺼져 있거나 재시작돼도 다시 접속을 시도한다.
    """
    client: LcuClient | None = None
    last_sig: tuple | None = None
    try:
        while True:
            if client is None:
                creds = find_credentials()
                if creds is None:
                    await asyncio.sleep(3.0)
                    continue
                client = LcuClient(creds)
            try:
                session = await client.champ_select_session()
            except (httpx.TransportError, httpx.HTTPStatusError) as e:
                log.info("LCU 연결 끊김 (%s), 재접속 대기", e)
                await client.aclose()
                client = None
                await asyncio.sleep(3.0)
                continue

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
    finally:
        if client is not None:
            await client.aclose()
