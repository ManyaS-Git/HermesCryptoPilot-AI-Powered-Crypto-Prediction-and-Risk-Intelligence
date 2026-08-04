"""Evaluation Agent: calibrates ensemble probabilities using real outcome
history (Platt scaling + shrinkage)."""
from __future__ import annotations

import numpy as np

from app.domain.prediction import CalibratedPrediction, EnsemblePrediction
from app.services.prediction.calibration import expected_calibrated_probability


class EvaluationAgent:
    async def calibrate(
        self,
        prediction: EnsemblePrediction,
        history_probs: np.ndarray | None = None,
        history_outcomes: np.ndarray | None = None,
    ) -> CalibratedPrediction:
        history_probs = history_probs if history_probs is not None else np.array([])
        history_outcomes = history_outcomes if history_outcomes is not None else np.array([])

        calibrated, method, samples = expected_calibrated_probability(
            prediction.probability, history_probs, history_outcomes
        )

        return CalibratedPrediction(
            asset=prediction.asset,
            interval=prediction.interval,
            raw_probability=round(prediction.probability, 4),
            calibrated_probability=round(calibrated, 4),
            direction=prediction.direction,
            expected_return=prediction.expected_return,
            calibration_method=method,
            calibration_bins=0,
            sample_count=samples,
        )
