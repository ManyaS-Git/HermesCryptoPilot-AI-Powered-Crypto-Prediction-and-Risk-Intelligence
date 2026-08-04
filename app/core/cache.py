"""TTL cache with optional Redis backend and an in-memory fallback.

Provides a consistent async interface. Redis is used when REDIS_URL is set,
otherwise a thread-safe in-memory LRU/TTL store keeps the app dependency-free.
"""
from __future__ import annotations

import asyncio
import json
import time
from collections import OrderedDict
from typing import Any, Callable, Optional

from app.core.config import get_settings


class MemoryCache:
    """Simple thread-safe TTL cache (LRU eviction)."""

    def __init__(self, capacity: int = 4096) -> None:
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._capacity = capacity
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at < time.monotonic():
                self._store.pop(key, None)
                return None
            self._store.move_to_end(key)
            return value

    async def set(self, key: str, value: Any, ttl: int) -> None:
        async with self._lock:
            self._store[key] = (time.monotonic() + ttl, value)
            self._store.move_to_end(key)
            while len(self._store) > self._capacity:
                self._store.popitem(last=False)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()


class RedisCache:
    def __init__(self, url: str) -> None:
        self._url = url
        self._redis = None

    async def _client(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = aioredis.from_url(self._url, decode_responses=True)
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self._client()
            raw = await client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int) -> None:
        try:
            client = await self._client()
            await client.set(key, json.dumps(value, default=str), ex=ttl)
        except Exception:
            pass

    async def delete(self, key: str) -> None:
        try:
            client = await self._client()
            await client.delete(key)
        except Exception:
            pass

    async def clear(self) -> None:
        try:
            client = await self._client()
            await client.flushdb()
        except Exception:
            pass


class Cache:
    """Unified cache facade used across the application."""

    def __init__(self) -> None:
        settings = get_settings()
        if settings.REDIS_URL:
            self._backend: Any = RedisCache(settings.REDIS_URL)
        else:
            self._backend = MemoryCache(settings.CACHE_DEFAULT_SIZE)
        self._default_ttl = settings.CACHE_TTL_SECONDS

    async def get(self, key: str) -> Optional[Any]:
        return await self._backend.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        await self._backend.set(key, value, ttl or self._default_ttl)

    async def delete(self, key: str) -> None:
        await self._backend.delete(key)

    async def clear(self) -> None:
        await self._backend.clear()

    async def get_or_set(
        self, key: str, factory: Callable[[], Any], ttl: Optional[int] = None
    ) -> Any:
        """Return the cached value or populate it via ``factory`` (async-safe)."""
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await factory() if asyncio.iscoroutinefunction(factory) else factory()
        if value is not None:
            await self.set(key, value, ttl)
        return value


_cache_instance: Optional[Cache] = None


def get_cache() -> Cache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = Cache()
    return _cache_instance
