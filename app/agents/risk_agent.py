"""Risk Agent: computes position sizing and risk metrics with the risk engine."""
from __future__ import annotations

from app.domain.fusion import SignalFusionResult
from app.domain.market import Candle
from app.domain.risk import PositionRecommendation, RiskMetrics
from app.services.risk.engine import RiskEngine


class RiskAgent:
    def __init__(self, engine: RiskEngine | None = None) -> None:
        self.engine = engine or RiskEngine()

    async def calculate_kelly_size(
        self, fusion_result: SignalFusionResult, candles: list[Candle], interval: str = "15m"
    ) -> tuple[PositionRecommendation, RiskMetrics]:
        return await self.engine.recommend(fusion_result, candles, interval)
