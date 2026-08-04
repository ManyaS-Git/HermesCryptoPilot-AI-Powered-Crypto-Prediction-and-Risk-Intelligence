"""Hyperliquid public API provider (perpetuals data)."""
from __future__ import annotations

from datetime import datetime, timezone

from app.domain.market import (
    Candle,
    FundingRate,
    OpenInterest,
    OrderBook,
    Ticker,
    Trade,
)
from app.services.market.base import MarketDataProvider, ProviderError
from app.services.market.clients import provider_get
from app.services.market.symbols import normalize_asset

BASE = "https://api.hyperliquid.xyz/info"


async def _post_info(payload: dict) -> dict:
    import httpx

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(BASE, json=payload)
        resp.raise_for_status()
        return resp.json()


class HyperliquidProvider(MarketDataProvider):
    name = "hyperliquid"
    supports_futures = True

    async def get_klines(self, asset: str, interval: str, limit: int = 500) -> list[Candle]:
        asset = normalize_asset(asset)
        resolution = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}.get(
            interval, "15m"
        )
        try:
            data = await _post_info(
                {"type": "candleSnapshot", "req": {"coin": asset, "interval": resolution, "limit": min(limit, 1000)}}
            )
            return [
                Candle(
                    timestamp=datetime.fromtimestamp(int(c[0]) / 1000, tz=timezone.utc),
                    open=float(c[1]), high=float(c[2]), low=float(c[3]),
                    close=float(c[4]), volume=float(c[5]),
                )
                for c in data
            ]
        except Exception as exc:
            raise ProviderError(f"Hyperliquid klines failed: {exc}") from exc

    async def get_ticker(self, asset: str) -> Ticker:
        asset = normalize_asset(asset)
        try:
            data = await _post_info({"type": "allMids"})
            price = float(data.get(asset, 0))
            if not price:
                raise ProviderError(f"Hyperliquid has no market for {asset}")
            meta = await _post_info({"type": "meta"})
            universe = meta.get("universe", [])
            name = next((u.get("name", asset) for u in universe if u.get("name") == asset), asset)
            return Ticker(
                symbol=asset,
                asset=asset,
                price=price,
                change_24h=0.0,
                change_pct_24h=0.0,
                volume_24h=0.0,
                high_24h=0.0,
                low_24h=0.0,
                source=self.name,
            )
        except Exception as exc:
            raise ProviderError(f"Hyperliquid ticker failed: {exc}") from exc

    async def get_funding_rate(self, asset: str) -> FundingRate | None:
        asset = normalize_asset(asset)
        try:
            data = await _post_info({"type": "metaAndAssetCtxs"})
            ctxs = data[1] if isinstance(data, list) and len(data) > 1 else []
            for ctx in ctxs:
                if ctx.get("coin") == asset:
                    return FundingRate(
                        symbol=asset,
                        asset=asset,
                        funding_rate=float(ctx.get("funding", 0)),
                        source=self.name,
                    )
            return None
        except Exception:
            return None

    async def get_open_interest(self, asset: str) -> OpenInterest | None:
        asset = normalize_asset(asset)
        try:
            data = await _post_info({"type": "metaAndAssetCtxs"})
            ctxs = data[1] if isinstance(data, list) and len(data) > 1 else []
            for ctx in ctxs:
                if ctx.get("coin") == asset:
                    oi = float(ctx.get("openInterest", 0))
                    price = float(ctx.get("markPx", 0))
                    return OpenInterest(
                        symbol=asset,
                        asset=asset,
                        open_interest=oi * price,
                        source=self.name,
                    )
            return None
        except Exception:
            return None

    async def get_order_book(self, asset: str, limit: int = 20) -> OrderBook:
        asset = normalize_asset(asset)
        try:
            data = await _post_info({"type": "l2Book", "coin": asset})
            return OrderBook(
                symbol=asset,
                bids=[{"price": float(l["px"]), "quantity": float(l["sz"])} for l in data.get("levels", [[]])[0][:limit]],
                asks=[{"price": float(l["px"]), "quantity": float(l["sz"])} for l in data.get("levels", [[], []])[1][:limit]],
                source=self.name,
            )
        except Exception as exc:
            raise ProviderError(f"Hyperliquid order book failed: {exc}") from exc

    async def get_recent_trades(self, asset: str, limit: int = 100) -> list[Trade]:
        asset = normalize_asset(asset)
        try:
            data = await _post_info({"type": "recentTrades", "coin": asset})
            return [
                Trade(
                    symbol=asset,
                    price=float(t["px"]),
                    quantity=float(t["sz"]),
                    side="buy" if t.get("side") == "B" else "sell",
                    timestamp=datetime.fromtimestamp(t["time"] / 1000, tz=timezone.utc),
                    source=self.name,
                )
                for t in data[:limit]
            ]
        except Exception as exc:
            raise ProviderError(f"Hyperliquid trades failed: {exc}") from exc
