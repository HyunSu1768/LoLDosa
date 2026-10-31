"""Riot API 레이트 리밋.

Riot은 응답 헤더로 한도를 알려준다. 예: ``X-App-Rate-Limit: 20:1,100:120``
(1초에 20회, 120초에 100회). 앱 단위와 메서드 단위 한도가 따로 있어서
버킷을 키별로 관리하고, 헤더를 받을 때마다 한도를 갱신한다.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Callable

# 개발용 키 기본값. 첫 응답의 헤더로 덮어쓴다.
DEFAULT_APP_LIMITS: list[tuple[int, float]] = [(20, 1.0), (100, 120.0)]


def parse_limits(header: str | None) -> list[tuple[int, float]]:
    """"20:1,100:120" -> [(20, 1.0), (100, 120.0)]"""
    if not header:
        return []
    out: list[tuple[int, float]] = []
    for part in header.split(","):
        count, _, window = part.strip().partition(":")
        if count and window:
            out.append((int(count), float(window)))
    return out


class SlidingWindowLimiter:
    """여러 (횟수, 초) 창을 동시에 지키는 슬라이딩 윈도우 리미터."""

    def __init__(
        self,
        limits: list[tuple[int, float]],
        clock: Callable[[], float] = time.monotonic,
        safety: float = 0.05,
    ) -> None:
        self._clock = clock
        self._safety = safety
        self._lock = asyncio.Lock()
        self._history: deque[float] = deque()
        self._blocked_until = 0.0
        self.set_limits(limits)

    @property
    def limits(self) -> list[tuple[int, float]]:
        return list(self._limits)

    def set_limits(self, limits: list[tuple[int, float]]) -> None:
        self._limits = sorted(limits, key=lambda x: x[1])

    def block_for(self, seconds: float) -> None:
        """429 Retry-After 처리."""
        self._blocked_until = max(self._blocked_until, self._clock() + seconds)

    def wait_time(self) -> float:
        """지금 요청하려면 몇 초 기다려야 하는지 (0이면 바로 가능)."""
        now = self._clock()
        wait = max(0.0, self._blocked_until - now)
        longest = self._limits[-1][1] if self._limits else 0.0
        while self._history and now - self._history[0] >= longest:
            self._history.popleft()
        for count, window in self._limits:
            recent = [t for t in self._history if now - t < window]
            if len(recent) >= count:
                # 가장 오래된 요청이 창 밖으로 나갈 때까지
                oldest = recent[len(recent) - count]
                wait = max(wait, oldest + window - now + self._safety)
        return wait

    async def acquire(self) -> None:
        async with self._lock:
            while (wait := self.wait_time()) > 0:
                await asyncio.sleep(wait)
            self._history.append(self._clock())
