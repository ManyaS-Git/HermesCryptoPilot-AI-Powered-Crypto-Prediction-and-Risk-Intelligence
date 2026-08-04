"""Ensemble prediction engine.

Trains multiple models on real historical candles, combines them with
performance-based weights, and produces a probability distribution over the
horizon (direction, expected return, confidence interval).

Walk-forward integrity: models are trained only on data strictly before the
prediction point, and holdout performance on the most recent tail is used to
weight ensemble members. No leakage, no random outputs.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from app.core.config import get_settings
from app.domain.market import Candle
from app.domain.prediction import EnsemblePrediction, ModelPrediction
from app.services.indicators.compute import candles_to_frame
from app.services.prediction.calibration import expected_calibrated_probability
from app.services.prediction.features import build_training_frame
from app.services.prediction.models import (
    GradientBoostedModel,
    LogisticModel,
    MomentumBaseline,
)

logger = logging.getLogger(__name__)


class PredictionEnsemble:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def predict(
        self,
        candles: list[Candle],
        asset: str,
        interval: str,
        horizon_bars: int = 1,
        history_probs: np.ndarray | None = None,
        history_outcomes: np.ndarray | None = None,
    ) -> EnsemblePrediction:
        df = candles_to_frame(candles)
        if len(df) < self.settings.FEATURE_WINDOW + 10:
            raise ValueError(
                f"Insufficient data ({len(df)} bars) for prediction; need >= "
                f"{self.settings.FEATURE_WINDOW + 10}"
            )

        # 1. Build labelled dataset
        X, y = build_training_frame(df, horizon_bars)
        train_size = max(int(len(X) * 0.8), 10)

        # 2. Train ensemble members
        models: list[BaseModel] = [MomentumBaseline()]
        if len(X) >= self.settings.ENSEMBLE_MIN_SAMPLES:
            if train_size >= 30:
                xgb = GradientBoostedModel()
                try:
                    xgb.fit(X.iloc[:train_size], y.iloc[:train_size])
                    if xgb._trained_samples > 30:  # noqa: SLF001
                        models.append(xgb)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("XGBoost training failed: %s", exc)

                logit = LogisticModel()
                try:
                    logit.fit(X.iloc[:train_size], y.iloc[:train_size])
                    models.append(logit)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Logistic training failed: %s", exc)

        # 3. Score ensemble members on the holdout tail
        holdout_X, holdout_y = X.iloc[train_size:], y.iloc[train_size:]
        weights: dict[str, float] = {}
        for model in models:
            if len(holdout_X) >= 5:
                acc = _holdout_accuracy(model, df, holdout_y, horizon_bars)
                weights[model.name] = max(acc, 0.5)
            else:
                weights[model.name] = 1.0
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}

        # 4. Generate member predictions at the current bar
        predictions: list[ModelPrediction] = []
        for model in models:
            proba = model.predict_proba_up(df, horizon_bars)
            direction = "UP" if proba >= 0.5 else "DOWN"
            expected_return = _safe_expected_return(model, df, horizon_bars)
            predictions.append(
                ModelPrediction(
                    model_name=model.name,
                    direction=direction,
                    probability=round(proba, 4),
                    expected_return=round(expected_return, 6),
                    prediction=None,
                    sample_count=_samples_for(model, df),
                )
            )

        # 5. Combine into an ensemble probability
        prob_up = sum(p.probability * weights[p.model_name] for p in predictions)
        prob_up = float(np.clip(prob_up, 0.01, 0.99))
        direction = "UP" if prob_up >= 0.5 else "DOWN"
        expected_return = sum(p.expected_return * weights[p.model_name] for p in predictions)

        # 6. Confidence interval from realised returns over the horizon
        lo, hi = _confidence_interval(df, horizon_bars, expected_return)

        last_close = float(df["close"].iloc[-1])
        expected_price = last_close * np.exp(expected_return)
        price_lo = last_close * np.exp(lo)
        price_hi = last_close * np.exp(hi)

        # 7. Calibrate the ensemble probability with outcome history
        calibrated = prob_up
        cal_method = "ensemble"
        cal_samples = 0
        if history_probs is not None and history_outcomes is not None:
            calibrated, cal_method, cal_samples = expected_calibrated_probability(
                prob_up, history_probs, history_outcomes
            )

        logger.info(
            "Ensemble %s prob_up=%.3f cal=%.3f weights=%s",
            asset, prob_up, calibrated, {k: round(v, 3) for k, v in weights.items()},
        )

        return EnsemblePrediction(
            asset=asset.upper(),
            interval=interval,
            horizon_bars=horizon_bars,
            direction=direction,
            probability=round(calibrated, 4),
            expected_return=round(expected_return, 6),
            expected_price=round(float(expected_price), 6),
            confidence_lower=round(float(price_lo), 6),
            confidence_upper=round(float(price_hi), 6),
            model_weights={k: round(v, 4) for k, v in weights.items()},
            model_predictions=predictions,
            feature_count=int(X.shape[1]),
        )


def _holdout_accuracy(model, df: pd.DataFrame, holdout_y: pd.Series, horizon: int) -> float:
    try:
        n = len(holdout_y)
        if n < 5:
            return 0.5
        correct = 0
        for i in range(n):
            sub = df.iloc[: len(df) - n + i + 1]
            if len(sub) < 30:
                continue
            p = model.predict_proba_up(sub, horizon)
            pred = 1 if p >= 0.5 else 0
            actual = 1 if holdout_y.iloc[i] > 0 else 0
            if pred == actual:
                correct += 1
        return correct / n
    except Exception:
        return 0.5


def _safe_expected_return(model, df: pd.DataFrame, horizon: int) -> float:
    try:
        value = model.expected_return(df, horizon)
        return float(value) if np.isfinite(value) else 0.0
    except Exception:
        return 0.0


def _samples_for(model, df: pd.DataFrame) -> int:
    return max(0, int(len(df) * 0.8) if "baseline" not in model.name else int(len(df)))


def _confidence_interval(
    df: pd.DataFrame, horizon: int, expected_return: float, conf: float = 0.8
) -> tuple[float, float]:
    window = df["close"].pct_change().dropna().tail(120)
    if window.empty:
        return expected_return - 0.05, expected_return + 0.05
    # Bootstrap the cumulative horizon return distribution
    rng = np.random.default_rng(42)
    cum = np.cumsum(window.sample(n=min(500, max(100, len(window))), replace=True).to_numpy())
    samples = np.array([np.sum(rng.choice(window.to_numpy(), size=horizon, replace=True)) for _ in range(1000)])
    lo = float(np.quantile(samples, (1 - conf) / 2))
    hi = float(np.quantile(samples, 1 - (1 - conf) / 2))
    return lo, hi


from typing import TYPE_CHECKING  # noqa: E402

if TYPE_CHECKING:
    from app.services.prediction.models import BaseModel
