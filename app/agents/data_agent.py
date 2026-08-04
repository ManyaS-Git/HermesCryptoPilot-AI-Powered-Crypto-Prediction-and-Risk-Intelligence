"""Market Data Agent: fetches real multi-timeframe OHLCV data and computes
technical indicators and market regime from it."""
from __future__ import annotations

from app.domain.market import Candle
from app.services.indicators.compute import candles_to_frame, compute_all, detect_regime
from app.services.market.manager import MarketDataManager


class MarketDataAgent:
    def __init__(self, market: MarketDataManager | None = None) -> None:
        self.market = market or MarketDataManager()

    async def fetch_historical_data(
        self, asset: str, timeframes: list[str] | None = None, limit: int = 500
    ) -> dict[str, list[Candle]]:
        timeframes = timeframes or ["5m", "15m", "1h"]
        data: dict[str, list[Candle]] = {}
        for tf in timeframes:
            try:
                data[tf] = await self.market.get_klines(asset, tf, limit)
            except Exception:
                continue
        return data

    async def get_indicators(self, asset: str, interval: str = "15m", limit: int = 500) -> dict:
        candles = await self.market.get_klines(asset, interval, limit)
        frame = candles_to_frame(candles)
        analysis = compute_all(frame)
        regime = detect_regime(frame)
        return {
            "asset": asset.upper(),
            "interval": interval,
            "latest": analysis["latest"],
            "series": analysis["series"],
            "regime": regime,
            "last_close": float(frame["close"].iloc[-1]) if len(frame) else None,
            "last_timestamp": frame["timestamp"].iloc[-1].isoformat() if len(frame) else None,
        }
