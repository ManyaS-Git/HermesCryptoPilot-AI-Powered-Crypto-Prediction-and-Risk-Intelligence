"""Shared async HTTP client for outbound provider calls."""
from __future__ import annotations

import httpx

from app.core.rate_limit import SlidingWindowRateLimiter, get_rate_limiter

_TIMEOUT = httpx.Timeout(20.0, connect=10.0)


async def provider_get(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    provider: str = "default",
    rps: int = 10,
    retries: int = 2,
) -> httpx.Response:
    """GET with per-provider rate limiting and bounded retries.

    Raises httpx.HTTPStatusError for non-2xx responses so callers can
    implement fallback chains.
    """
    limiter = get_rate_limiter()
    last_exc: Exception | None = None
    async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
        for attempt in range(retries + 1):
            await limiter.acquire(f"provider:{provider}")
            try:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                return resp
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if attempt < retries:
                    await _sleep(0.5 * (attempt + 1))
    raise last_exc  # type: ignore[misc]


async def _sleep(seconds: float) -> None:
    import asyncio

    await asyncio.sleep(seconds)
