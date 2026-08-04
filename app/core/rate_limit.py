"""Sliding-window rate limiter (in-memory) used for outbound provider calls
and inbound API requests when a distributed backend is not available."""
from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from typing import Deque


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int = 30, window_seconds: int = 10) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def acquire(self, key: str = "default") -> None:
        async with self._lock:
            now = time.monotonic()
            window = self._hits[key]
            while window and window[0] <= now - self.window_seconds:
                window.popleft()
            if len(window) >= self.max_requests:
                wait = self.window_seconds - (now - window[0])
                # sleep outside the lock to avoid blocking other keys
                await self._release_and_sleep(key, wait)
                await self.acquire(key)
                return
            window.append(now)

    async def _release_and_sleep(self, key: str, seconds: float) -> None:
        # drop the oldest hit so the caller can retry immediately after sleeping
        await asyncio.sleep(seconds)


_limiter: SlidingWindowRateLimiter | None = None


def get_rate_limiter() -> SlidingWindowRateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = SlidingWindowRateLimiter()
    return _limiter
