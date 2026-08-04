"""Market data manager: routing, caching, and cross-provider fallback.

Resilience strategy:
1. Try providers in priority order until one succeeds.
2. Cache successful responses for TTL to absorb rate limits.
3. Never fabricate data — if every provider fails, raise ProviderError
   and let the API layer return a proper error/empty state.
"""
from __future__ import annotations

from typing import Any

from app.core.cache import get_cache
from app.core.config import get_settings
from app.domain.market import (
    AssetInfo,
    Candle,
    FearGreedValue,
    FundingRate,
    Liquidation,
    OnChainMetrics,
    OpenInterest,
    OrderBook,
    Ticker,
    Trade,
)
from app.services.market.base import MarketDataProvider, ProviderError
from app.services.market.binance import BinanceProvider
from app.services.market.bybit import BybitProvider
from app.services.market.coingecko import CoinGeckoProvider
from app.services.market.hyperliquid import HyperliquidProvider
from app.services.market.kraken import KrakenProvider


class MarketDataManager:
    def __init__(self) -> None:
        self.binance = BinanceProvider()
        self.hyperliquid = HyperliquidProvider()
        self.bybit = BybitProvider()
        self.kraken = KrakenProvider()
        self.coingecko = CoinGeckoProvider()
        self.provider_chain: list[MarketDataProvider] = [
            self.binance,
            self.hyperliquid,
            self.bybit,
            self.kraken,
        ]
        self.cache = get_cache()

    def _key(self, *parts: str) -> str:
        return "mkt:" + ":".join(parts)

    async def _fetch_with_fallback(
        self, method: str, asset: str, *args: Any, **kwargs: Any
    ) -> Any:
        errors: list[str] = []
        for provider in self.provider_chain:
            try:
                fn = getattr(provider, method)
                if asset:
                    result = await fn(asset, *args, **kwargs)
                else:
                    result = await fn(*args, **kwargs)
                if result is not None:
                    return result
            except (ProviderError, Exception) as exc:  # noqa: BLE001
                errors.append(f"{provider.name}: {exc}")
        raise ProviderError(f"All providers failed for {method}({asset}): {'; '.join(errors)}")

    # --- Candle / price history ---
    async def get_klines(
        self, asset: str, interval: str = "15m", limit: int = 500
    ) -> list[Candle]:
        cache_key = self._key("klines", asset.upper(), interval, str(limit))
        cached = await self.cache.get(cache_key)
        if cached:
            return [Candle.model_validate(c) for c in cached]
        data = await self._fetch_with_fallback("get_klines", asset, interval, limit)
        await self.cache.set(
            cache_key, [c.model_dump() for c in data], ttl=_ttl_for(interval)
        )
        return data

    # --- Tickers ---
    async def get_ticker(self, asset: str) -> Ticker:
        cache_key = self._key("ticker", asset.upper())
        cached = await self.cache.get(cache_key)
        if cached:
            return Ticker.model_validate(cached)
        data = await self._fetch_with_fallback("get_ticker", asset)
        await self.cache.set(cache_key, data.model_dump(), ttl=30)
        return data

    async def get_tickers(self) -> list[Ticker]:
        cache_key = self._key("tickers")
        cached = await self.cache.get(cache_key)
        if cached:
            return [Ticker.model_validate(t) for t in cached]
        tickers = await self.binance.get_tickers()
        await self.cache.set(cache_key, [t.model_dump() for t in tickers], ttl=30)
        return tickers

    # --- Derivatives ---
    async def get_funding_rate(self, asset: str) -> FundingRate | None:
        cache_key = self._key("funding", asset.upper())
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return FundingRate.model_validate(cached) if cached else None
        try:
            result = await self._fetch_with_fallback("get_funding_rate", asset)
            await self.cache.set(cache_key, result.model_dump() if result else None, ttl=60)
            return result
        except ProviderError:
            return None

    async def get_open_interest(self, asset: str) -> OpenInterest | None:
        cache_key = self._key("oi", asset.upper())
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return OpenInterest.model_validate(cached) if cached else None
        try:
            result = await self._fetch_with_fallback("get_open_interest", asset)
            await self.cache.set(cache_key, result.model_dump() if result else None, ttl=60)
            return result
        except ProviderError:
            return None

    async def get_order_book(self, asset: str, limit: int = 20) -> OrderBook:
        cache_key = self._key("ob", asset.upper(), str(limit))
        cached = await self.cache.get(cache_key)
        if cached:
            return OrderBook.model_validate(cached)
        data = await self._fetch_with_fallback("get_order_book", asset, limit)
        await self.cache.set(cache_key, data.model_dump(), ttl=15)
        return data

    async def get_recent_trades(self, asset: str, limit: int = 100) -> list[Trade]:
        cache_key = self._key("trades", asset.upper(), str(limit))
        cached = await self.cache.get(cache_key)
        if cached:
            return [Trade.model_validate(t) for t in cached]
        data = await self._fetch_with_fallback("get_recent_trades", asset, limit)
        await self.cache.set(cache_key, [t.model_dump() for t in data], ttl=10)
        return data

    async def get_liquidations(self, asset: str) -> list[Liquidation]:
        try:
            return await self.binance.get_liquidations(asset)
        except Exception:
            return []

    # --- Universe ---
    async def get_assets(self, top: int = 50) -> list[AssetInfo]:
        cache_key = self._key("assets", str(top))
        cached = await self.cache.get(cache_key)
        if cached:
            return [AssetInfo.model_validate(a) for a in cached]
        data = await self.coingecko.get_assets(top=top)
        await self.cache.set(cache_key, [a.model_dump() for a in data], ttl=300)
        return data

    async def get_fear_greed(self) -> FearGreedValue | None:
        cache_key = self._key("fng")
        cached = await self.cache.get(cache_key)
        if cached:
            return FearGreedValue.model_validate(cached)
        data = await self.coingecko.get_fear_greed()
        await self.cache.set(cache_key, data.model_dump() if data else None, ttl=3600)
        return data

    async def get_on_chain(self, asset: str) -> OnChainMetrics | None:
        try:
            return await self.binance.get_on_chain(asset)
        except Exception:
            return None


def _ttl_for(interval: str) -> int:
    mapping = {"1m": 30, "5m": 45, "15m": 60, "1h": 180, "4h": 600, "1d": 1800}
    return mapping.get(interval, 60)


_market_manager: MarketDataManager | None = None


def get_market_manager() -> MarketDataManager:
    global _market_manager
    if _market_manager is None:
        _market_manager = MarketDataManager()
    return _market_manager
