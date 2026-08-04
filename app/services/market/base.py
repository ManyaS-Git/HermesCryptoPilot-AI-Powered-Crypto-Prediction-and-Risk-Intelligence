from __future__ import annotations

from abc import ABC, abstractmethod

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


class ProviderError(Exception):
    """Raised when an upstream market data provider fails."""


class MarketDataProvider(ABC):
    name: str = "base"
    supports_futures: bool = False
    supports_on_chain: bool = False

    @abstractmethod
    async def get_klines(
        self, asset: str, interval: str, limit: int = 500
    ) -> list[Candle]:
        ...

    @abstractmethod
    async def get_ticker(self, asset: str) -> Ticker:
        ...

    async def get_tickers(self) -> list[Ticker]:
        raise ProviderError(f"{self.name} does not support bulk tickers")

    async def get_funding_rate(self, asset: str) -> FundingRate | None:
        raise ProviderError(f"{self.name} does not support funding rates")

    async def get_open_interest(self, asset: str) -> OpenInterest | None:
        raise ProviderError(f"{self.name} does not support open interest")

    async def get_order_book(self, asset: str, limit: int = 20) -> OrderBook:
        raise ProviderError(f"{self.name} does not support order book")

    async def get_recent_trades(self, asset: str, limit: int = 100) -> list[Trade]:
        raise ProviderError(f"{self.name} does not support trades")

    async def get_liquidations(self, asset: str) -> list[Liquidation]:
        raise ProviderError(f"{self.name} does not support liquidations")

    async def get_assets(self) -> list[AssetInfo]:
        raise ProviderError(f"{self.name} does not support asset listings")

    async def get_fear_greed(self) -> FearGreedValue | None:
        raise ProviderError(f"{self.name} does not support fear & greed")

    async def get_on_chain(self, asset: str) -> OnChainMetrics | None:
        raise ProviderError(f"{self.name} does not support on-chain data")

    async def health_check(self) -> bool:
        try:
            await self.get_ticker("BTC")
            return True
        except Exception:
            return False
