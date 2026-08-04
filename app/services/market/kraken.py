"""Kraken public API provider (spot)."""
from __future__ import annotations

from datetime import datetime, timezone

from app.domain.market import Candle, OrderBook, Ticker
from app.services.market.base import MarketDataProvider, ProviderError
from app.services.market.clients import provider_get
from app.services.market.symbols import kraken_pair, normalize_asset

BASE = "https://api.kraken.com/0/public"

INTERVAL_MAP = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "4h": 240, "1d": 1440}


class KrakenProvider(MarketDataProvider):
    name = "kraken"

    async def get_klines(self, asset: str, interval: str, limit: int = 500) -> list[Candle]:
        pair = kraken_pair(asset)
        itv = INTERVAL_MAP.get(interval, 15)
        try:
            resp = await provider_get(
                f"{BASE}/OHLC", params={"pair": pair, "interval": itv}, provider="kraken", rps=5
            )
            data = resp.json()
            result = data.get("result", {})
            if not result or "error" in result:
                raise ProviderError(f"Kraken klines error: {data.get('error')}")
            rows = next(iter(result.values()))
            return [
                Candle(
                    timestamp=datetime.fromtimestamp(r[0], tz=timezone.utc),
                    open=float(r[1]), high=float(r[2]), low=float(r[3]),
                    close=float(r[4]), volume=float(r[6]),
                )
                for r in rows[-limit:]
            ]
        except Exception as exc:
            raise ProviderError(f"Kraken klines failed: {exc}") from exc

    async def get_ticker(self, asset: str) -> Ticker:
        pair = kraken_pair(asset)
        try:
            resp = await provider_get(
                f"{BASE}/Ticker", params={"pair": pair}, provider="kraken", rps=5
            )
            data = resp.json()
            result = data.get("result", {})
            if not result:
                raise ProviderError(f"Kraken ticker error: {data.get('error')}")
            t = next(iter(result.values()))
            return Ticker(
                symbol=pair,
                asset=normalize_asset(asset),
                price=float(t["c"][0]),
                change_24h=float(t["p"][0]) - float(t["o"]),
                change_pct_24h=((float(t["p"][0]) / float(t["o"])) - 1) * 100 if float(t["o"]) else 0.0,
                volume_24h=float(t["v"][1]),
                high_24h=float(t["h"][1]),
                low_24h=float(t["l"][1]),
                source=self.name,
            )
        except Exception as exc:
            raise ProviderError(f"Kraken ticker failed: {exc}") from exc

    async def get_order_book(self, asset: str, limit: int = 20) -> OrderBook:
        pair = kraken_pair(asset)
        try:
            resp = await provider_get(
                f"{BASE}/Depth", params={"pair": pair, "count": min(limit, 100)}, provider="kraken", rps=5
            )
            data = resp.json()
            result = data.get("result", {})
            if not result:
                raise ProviderError(f"Kraken depth error: {data.get('error')}")
            book = next(iter(result.values()))
            return OrderBook(
                symbol=pair,
                bids=[{"price": float(b[0]), "quantity": float(b[1])} for b in book.get("bids", [])[:limit]],
                asks=[{"price": float(a[0]), "quantity": float(a[1])} for a in book.get("asks", [])[:limit]],
                source=self.name,
            )
        except Exception as exc:
            raise ProviderError(f"Kraken order book failed: {exc}") from exc
