"""Signal Fusion Agent: blends calibrated technicals, market consensus, and
news sentiment with dynamic weights."""
from __future__ import annotations

from app.domain.fusion import SignalFusionResult
from app.domain.intel import UnifiedMarketConsensus
from app.domain.news import SentimentResult
from app.domain.prediction import CalibratedPrediction
from app.services.fusion.fusion import SignalFusionEngine


class SignalFusionAgent:
    def __init__(self, engine: SignalFusionEngine | None = None) -> None:
        self.engine = engine or SignalFusionEngine()

    async def fuse_signals(
        self,
        technicals: CalibratedPrediction,
        consensus: UnifiedMarketConsensus,
        sentiment: SentimentResult | None = None,
        regime: dict | None = None,
        historical_accuracy: float | None = None,
    ) -> SignalFusionResult:
        return self.engine.fuse(
            technicals,
            consensus,
            sentiment,
            regime or {"regime": "unknown", "volatility": 0.0},
            historical_accuracy=historical_accuracy,
        )
