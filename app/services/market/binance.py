"""Binance market data provider (spot + USDT-margined futures).

Uses only public endpoints. Returns real exchange data.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.domain.market import (
    Candle,
    FundingRate,
    Liquidation,
    OpenInterest,
    OrderBook,
    Ticker,
    Trade,
)
from app.services.market.base import MarketDataProvider, ProviderError
from app.services.market.clients import provider_get
from app.services.market.symbols import usdt_pair

SPOT_BASE = "https://api.binance.com/api/v3"
FUTURES_BASE = "https://fapi.binance.com/fapi/v1"

INTERVAL_MAP = {
    "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m",
    "30m": "30m", "1h": "1h", "2h": "2h", "4h": "4h",
    "6h": "6h", "12h": "12h", "1d": "1d", "1w": "1w",
}


def _parse_klines(raw: list, symbol: str) -> list[Candle]:
    candles: list[Candle] = []
    for row in raw:
        candles.append(
            Candle(
                timestamp=datetime.fromtimestamp(row[0] / 1000, tz=timezone.utc),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
        )
    return candles


class BinanceProvider(MarketDataProvider):
    name = "binance"
    supports_futures = True

    async def get_klines(
        self, asset: str, interval: str, limit: int = 500
    ) -> list[Candle]:
        symbol = usdt_pair(asset)
        interval = INTERVAL_MAP.get(interval, "15m")
        try:
            resp = await provider_get(
                f"{SPOT_BASE}/klines",
                params={"symbol": symbol, "interval": interval, "limit": min(limit, 1000)},
                provider="binance",
            )
            return _parse_klines(resp.json(), symbol)
        except Exception as exc:
            raise ProviderError(f"Binance klines failed: {exc}") from exc

    async def get_ticker(self, asset: str) -> Ticker:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{SPOT_BASE}/ticker/24hr",
                params={"symbol": symbol},
                provider="binance",
            )
            data = resp.json()
            return Ticker(
                symbol=symbol,
                asset=asset.upper(),
                price=float(data["lastPrice"]),
                change_24h=float(data["priceChange"]),
                change_pct_24h=float(data["priceChangePercent"]),
                volume_24h=float(data["volume"]),
                high_24h=float(data["highPrice"]),
                low_24h=float(data["lowPrice"]),
                source=self.name,
            )
        except Exception as exc:
            raise ProviderError(f"Binance ticker failed: {exc}") from exc

    async def get_tickers(self) -> list[Ticker]:
        try:
            resp = await provider_get(
                f"{SPOT_BASE}/ticker/24hr", provider="binance", rps=8
            )
            tickers: list[Ticker] = []
            for d in resp.json():
                if not d["symbol"].endswith("USDT"):
                    continue
                asset = d["symbol"][:-4]
                tickers.append(
                    Ticker(
                        symbol=d["symbol"],
                        asset=asset,
                        price=float(d["lastPrice"]),
                        change_24h=float(d["priceChange"]),
                        change_pct_24h=float(d["priceChangePercent"]),
                        volume_24h=float(d["volume"]),
                        high_24h=float(d["highPrice"]),
                        low_24h=float(d["lowPrice"]),
                        source=self.name,
                    )
                )
            tickers.sort(key=lambda t: t.volume_24h, reverse=True)
            return tickers[:500]
        except Exception as exc:
            raise ProviderError(f"Binance tickers failed: {exc}") from exc

    async def get_funding_rate(self, asset: str) -> FundingRate | None:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{FUTURES_BASE}/premiumIndex",
                params={"symbol": symbol},
                provider="binance",
            )
            data = resp.json()
            if "lastFundingRate" not in data:
                return None
            return FundingRate(
                symbol=symbol,
                asset=asset.upper(),
                funding_rate=float(data["lastFundingRate"]),
                source=self.name,
            )
        except Exception:
            return None

    async def get_open_interest(self, asset: str) -> OpenInterest | None:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{FUTURES_BASE}/openInterest",
                params={"symbol": symbol},
                provider="binance",
            )
            data = resp.json()
            return OpenInterest(
                symbol=symbol,
                asset=asset.upper(),
                open_interest=float(data["openInterest"]),
                source=self.name,
            )
        except Exception:
            return None

    async def get_order_book(self, asset: str, limit: int = 20) -> OrderBook:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{SPOT_BASE}/depth",
                params={"symbol": symbol, "limit": min(limit, 500)},
                provider="binance",
            )
            data = resp.json()
            return OrderBook(
                symbol=symbol,
                bids=[{"price": float(b[0]), "quantity": float(b[1])} for b in data["bids"]],
                asks=[{"price": float(a[0]), "quantity": float(a[1])} for a in data["asks"]],
                source=self.name,
            )
        except Exception as exc:
            raise ProviderError(f"Binance order book failed: {exc}") from exc

    async def get_recent_trades(self, asset: str, limit: int = 100) -> list[Trade]:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{SPOT_BASE}/aggTrades",
                params={"symbol": symbol, "limit": min(limit, 1000)},
                provider="binance",
            )
            return [
                Trade(
                    symbol=symbol,
                    price=float(t["p"]),
                    quantity=float(t["q"]),
                    side="buy" if not t["m"] else "sell",
                    timestamp=datetime.fromtimestamp(t["T"] / 1000, tz=timezone.utc),
                    source=self.name,
                )
                for t in resp.json()
            ]
        except Exception as exc:
            raise ProviderError(f"Binance trades failed: {exc}") from exc

    async def get_liquidations(self, asset: str) -> list[Liquidation]:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{FUTURES_BASE}/allForceOrders",
                params={"symbol": symbol, "limit": 100},
                provider="binance",
            )
            out: list[Liquidation] = []
            for f in resp.json():
                out.append(
                    Liquidation(
                        symbol=symbol,
                        price=float(f["price"]),
                        quantity=float(f["origQty"]),
                        side="long" if f["side"] == "SELL" else "short",
                        timestamp=datetime.fromtimestamp(f["time"] / 1000, tz=timezone.utc),
                        source=self.name,
                    )
                )
            return out
        except Exception:
            return []
