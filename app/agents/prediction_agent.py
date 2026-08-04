"""Prediction Agent: runs the real ensemble prediction engine."""
from __future__ import annotations

from app.domain.prediction import EnsemblePrediction
from app.services.prediction.ensemble import PredictionEnsemble


class PredictionAgent:
    def __init__(self, ensemble: PredictionEnsemble | None = None) -> None:
        self.ensemble = ensemble or PredictionEnsemble()

    async def run_prediction(
        self,
        asset: str,
        candles,
        interval: str = "15m",
        horizon_bars: int = 1,
        history_probs=None,
        history_outcomes=None,
    ) -> EnsemblePrediction:
        return await self.ensemble.predict(
            candles,
            asset=asset,
            interval=interval,
            horizon_bars=horizon_bars,
            history_probs=history_probs,
            history_outcomes=history_outcomes,
        )
