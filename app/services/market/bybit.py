"""Bybit public API provider (spot + linear perpetuals)."""
from __future__ import annotations

from datetime import datetime, timezone

from app.domain.market import Candle, FundingRate, OpenInterest, OrderBook, Ticker, Trade
from app.services.market.base import MarketDataProvider, ProviderError
from app.services.market.clients import provider_get
from app.services.market.symbols import usdt_pair

BASE = "https://api.bybit.com/v5/market"


class BybitProvider(MarketDataProvider):
    name = "bybit"
    supports_futures = True

    async def get_klines(self, asset: str, interval: str, limit: int = 500) -> list[Candle]:
        symbol = usdt_pair(asset)
        category = "linear"
        itv = {"1m": "1", "5m": "5", "15m": "15", "30m": "30", "1h": "60", "4h": "240", "1d": "D"}.get(interval, "15")
        try:
            resp = await provider_get(
                f"{BASE}/kline",
                params={"category": category, "symbol": symbol, "interval": itv, "limit": min(limit, 1000)},
                provider="bybit", rps=8,
            )
            result = resp.json().get("result", {})
            rows = result.get("list", [])
            return [
                Candle(
                    timestamp=datetime.fromtimestamp(int(r[0]) / 1000, tz=timezone.utc),
                    open=float(r[1]), high=float(r[2]), low=float(r[3]),
                    close=float(r[4]), volume=float(r[5]),
                )
                for r in rows
            ]
        except Exception as exc:
            raise ProviderError(f"Bybit klines failed: {exc}") from exc

    async def get_ticker(self, asset: str) -> Ticker:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{BASE}/tickers", params={"category": "spot", "symbol": symbol}, provider="bybit", rps=8
            )
            t = resp.json()["result"]["list"][0]
            return Ticker(
                symbol=symbol,
                asset=asset.upper(),
                price=float(t["lastPrice"]),
                change_24h=float(t["price24hPcnt"]) * float(t["lastPrice"]),
                change_pct_24h=float(t["price24hPcnt"]) * 100,
                volume_24h=float(t["volume24h"]),
                high_24h=float(t["highPrice24h"]),
                low_24h=float(t["lowPrice24h"]),
                source=self.name,
            )
        except Exception as exc:
            raise ProviderError(f"Bybit ticker failed: {exc}") from exc

    async def get_funding_rate(self, asset: str) -> FundingRate | None:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{BASE}/funding/history",
                params={"category": "linear", "symbol": symbol, "limit": 1},
                provider="bybit", rps=8,
            )
            rows = resp.json().get("result", {}).get("list", [])
            if not rows:
                return None
            return FundingRate(
                symbol=symbol, asset=asset.upper(),
                funding_rate=float(rows[0]["fundingRate"]), source=self.name,
            )
        except Exception:
            return None

    async def get_open_interest(self, asset: str) -> OpenInterest | None:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{BASE}/open-interest",
                params={"category": "linear", "symbol": symbol, "intervalTime": "1h", "limit": 1},
                provider="bybit", rps=8,
            )
            rows = resp.json().get("result", {}).get("list", [])
            if not rows:
                return None
            return OpenInterest(
                symbol=symbol, asset=asset.upper(),
                open_interest=float(rows[0]["openInterest"]), source=self.name,
            )
        except Exception:
            return None

    async def get_order_book(self, asset: str, limit: int = 20) -> OrderBook:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{BASE}/orderbook",
                params={"category": "spot", "symbol": symbol, "limit": min(limit, 500)},
                provider="bybit", rps=8,
            )
            result = resp.json().get("result", {})
            return OrderBook(
                symbol=symbol,
                bids=[{"price": float(b[0]), "quantity": float(b[1])} for b in result.get("b", [])],
                asks=[{"price": float(a[0]), "quantity": float(a[1])} for a in result.get("a", [])],
                source=self.name,
            )
        except Exception as exc:
            raise ProviderError(f"Bybit order book failed: {exc}") from exc

    async def get_recent_trades(self, asset: str, limit: int = 100) -> list[Trade]:
        symbol = usdt_pair(asset)
        try:
            resp = await provider_get(
                f"{BASE}/recent-trade",
                params={"category": "spot", "symbol": symbol, "limit": min(limit, 100)},
                provider="bybit", rps=8,
            )
            rows = resp.json().get("result", {}).get("list", [])
            return [
                Trade(
                    symbol=symbol,
                    price=float(r["price"]),
                    quantity=float(r["size"]),
                    side="buy" if r["side"] == "Buy" else "sell",
                    timestamp=datetime.fromtimestamp(int(r["time"]) / 1000, tz=timezone.utc),
                    source=self.name,
                )
                for r in rows
            ]
        except Exception as exc:
            raise ProviderError(f"Bybit trades failed: {exc}") from exc
