"""Riot 웹 API 클라이언트 (지식 베이스 수집용).

챔피언 선택 화면 자체는 LCU(로컬)에서 읽고, 이 클라이언트는 오프라인 수집
파이프라인에서만 쓴다.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from .ratelimit import DEFAULT_APP_LIMITS, SlidingWindowLimiter, parse_limits

log = logging.getLogger(__name__)

QUEUE_SOLO = "RANKED_SOLO_5x5"


class RiotApiError(RuntimeError):
    def __init__(self, status: int, url: str, body: str) -> None:
        super().__init__(f"Riot API {status} for {url}: {body[:200]}")
        self.status = status


class RiotClient:
    def __init__(
        self,
        api_key: str,
        platform: str = "kr",
        region: str = "asia",
        transport: httpx.AsyncBaseTransport | None = None,
        max_retries: int = 4,
    ) -> None:
        if not api_key:
            raise ValueError("RIOT_API_KEY 가 없습니다. .env 를 확인하세요.")
        self.platform = platform
        self.region = region
        self.max_retries = max_retries
        self._http = httpx.AsyncClient(
            headers={"X-Riot-Token": api_key},
            timeout=15.0,
            transport=transport,
        )
        self._app_limiter = SlidingWindowLimiter(DEFAULT_APP_LIMITS)
        self._method_limiters: dict[str, SlidingWindowLimiter] = {}

    async def __aenter__(self) -> "RiotClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    # ---- low level -------------------------------------------------------

    async def _get(self, host: str, method: str, path: str, params: dict | None = None) -> Any:
        url = f"https://{host}.api.riotgames.com{path}"
        method_limiter = self._method_limiters.setdefault(method, SlidingWindowLimiter([]))
        for attempt in range(self.max_retries + 1):
            await self._app_limiter.acquire()
            await method_limiter.acquire()
            try:
                resp = await self._http.get(url, params=params)
            except httpx.TransportError as e:
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(2**attempt)
                log.warning("transport error %s, retrying", e)
                continue

            if limits := parse_limits(resp.headers.get("X-App-Rate-Limit")):
                self._app_limiter.set_limits(limits)
            if limits := parse_limits(resp.headers.get("X-Method-Rate-Limit")):
                method_limiter.set_limits(limits)

            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", 2 ** (attempt + 1)))
                scope = resp.headers.get("X-Rate-Limit-Type", "app")
                (method_limiter if scope == "method" else self._app_limiter).block_for(retry_after)
                log.warning("429 (%s), waiting %.1fs", scope, retry_after)
                continue
            if resp.status_code >= 500 and attempt < self.max_retries:
                await asyncio.sleep(2**attempt)
                continue
            if resp.status_code == 404:
                return None
            if resp.status_code >= 400:
                raise RiotApiError(resp.status_code, url, resp.text)
            return resp.json()
        raise RiotApiError(429, url, "retries exhausted")

    # ---- league (플랫폼 라우팅: kr) ---------------------------------------

    async def apex_league(self, tier: str, queue: str = QUEUE_SOLO) -> dict:
        """tier: challenger | grandmaster | master"""
        path = f"/lol/league/v4/{tier.lower()}leagues/by-queue/{queue}"
        return await self._get(self.platform, f"league-{tier}", path)

    async def league_entries(
        self, tier: str, division: str, page: int = 1, queue: str = QUEUE_SOLO
    ) -> list[dict]:
        """플래티넘 등 일반 티어. tier=PLATINUM, division=I..IV"""
        path = f"/lol/league/v4/entries/{queue}/{tier.upper()}/{division}"
        return await self._get(self.platform, "league-entries", path, {"page": page}) or []

    # ---- match (리전 라우팅: asia) ----------------------------------------

    async def match_ids(
        self, puuid: str, queue: int = 420, count: int = 20, start_time: int | None = None
    ) -> list[str]:
        params: dict[str, Any] = {"queue": queue, "count": count}
        if start_time is not None:
            params["startTime"] = start_time
        path = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        return await self._get(self.region, "match-ids", path, params) or []

    async def match(self, match_id: str) -> dict | None:
        return await self._get(self.region, "match", f"/lol/match/v5/matches/{match_id}")

    async def timeline(self, match_id: str) -> dict | None:
        path = f"/lol/match/v5/matches/{match_id}/timeline"
        return await self._get(self.region, "timeline", path)
