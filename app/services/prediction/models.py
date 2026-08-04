"""Prediction models used in the ensemble.

- ``GradientBoostedModel``: XGBoost classifier on engineered features.
- ``LogisticModel``: regularized logistic regression (fast baseline).
- ``MomentumBaseline``: deterministic statistical model based on EMA
  crossovers and momentum — used as a robust fallback when there is not
  enough data to train a supervised model.

Every model exposes ``predict_proba_up(df)`` returning a probability that
the price moves up over the horizon.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from app.services.prediction.features import build_feature_frame, create_labels

logger = logging.getLogger(__name__)
RNG = np.random.default_rng(42)


class BaseModel(ABC):
    name: str = "base"

    @abstractmethod
    def predict_proba_up(self, df: pd.DataFrame, horizon: int = 1) -> float:
        """Probability the price is higher after ``horizon`` bars."""
        ...

    def expected_return(self, df: pd.DataFrame, horizon: int = 1) -> float:
        """Best-effort expected log-return over the horizon."""
        raise NotImplementedError


class GradientBoostedModel(BaseModel):
    name = "xgboost"

    def __init__(self) -> None:
        self._model = None
        self._feature_cols: list[str] | None = None
        self._trained_samples = 0

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        from xgboost import XGBClassifier

        binary = (y > 0).astype(int)
        model = XGBClassifier(
            n_estimators=120,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=2,
        )
        model.fit(X, binary)
        self._model = model
        self._feature_cols = list(X.columns)
        self._trained_samples = int(len(X))

    def predict_proba_up(self, df: pd.DataFrame, horizon: int = 1) -> float:
        if self._model is None or self._feature_cols is None:
            return 0.5
        features = build_feature_frame(df)
        if features.empty:
            return 0.5
        row = features.iloc[[-1]][self._feature_cols]
        proba = float(self._model.predict_proba(row.values)[0][1])
        return max(0.001, min(0.999, proba))

    def expected_return(self, df: pd.DataFrame, horizon: int = 1) -> float:
        labels = create_labels(df, horizon)
        window = labels.dropna().tail(50)
        if window.empty:
            return 0.0
        # Conditional on model conviction, average historical drift
        return float(np.mean(window)) if self._trained_samples > 0 else 0.0


class LogisticModel(BaseModel):
    name = "logistic_regression"

    def __init__(self) -> None:
        self._model = None
        self._scaler = None
        self._feature_cols: list[str] | None = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler

        binary = (y > 0).astype(int)
        if binary.nunique() < 2:
            return
        scaler = StandardScaler()
        Xs = scaler.fit_transform(X.values)
        model = LogisticRegression(C=0.1, max_iter=1000, class_weight="balanced")
        model.fit(Xs, binary)
        self._model = model
        self._scaler = scaler
        self._feature_cols = list(X.columns)

    def predict_proba_up(self, df: pd.DataFrame, horizon: int = 1) -> float:
        if self._model is None or self._scaler is None or self._feature_cols is None:
            return 0.5
        features = build_feature_frame(df)
        if features.empty:
            return 0.5
        row = self._scaler.transform(features.iloc[[-1]][self._feature_cols].values)
        proba = float(self._model.predict_proba(row)[0][1])
        return max(0.001, min(0.999, proba))


class MomentumBaseline(BaseModel):
    """Deterministic statistical model — no training required.

    Blends short/long EMA alignment and realised momentum into a probability
    via a soft assignment. Fully explainable and real.
    """

    name = "momentum_baseline"

    def predict_proba_up(self, df: pd.DataFrame, horizon: int = 1) -> float:
        if len(df) < 30:
            return 0.5
        close = df["close"]
        ema_fast = close.ewm(span=8, adjust=False).mean()
        ema_slow = close.ewm(span=26, adjust=False).mean()

        cross = (ema_fast.iloc[-1] - ema_slow.iloc[-1]) / close.iloc[-1]
        mom_10 = close.iloc[-1] / close.iloc[-10] - 1.0
        mom_30 = close.iloc[-1] / close.iloc[-30] - 1.0 if len(close) >= 30 else mom_10
        recent_std = close.pct_change().tail(20).std() * np.sqrt(horizon)

        # Fisher-like combination: strength from crossovers + momentum
        signal = np.tanh(6.0 * cross + 3.0 * mom_10 + 1.5 * mom_30)
        # Scale by uncertainty (volatility): less confident in wild markets
        scale = 1.0 / (1.0 + recent_std * 10.0)
        proba = 0.5 + 0.5 * signal * scale
        return float(np.clip(proba, 0.05, 0.95))

    def expected_return(self, df: pd.DataFrame, horizon: int = 1) -> float:
        close = df["close"]
        window = close.pct_change().tail(50).dropna()
        if window.empty:
            return 0.0
        drift = float(window.mean() * horizon)
        proba = self.predict_proba_up(df, horizon)
        # Blend drift toward the model's directional conviction
        return float(drift * 0.5 + (proba - 0.5) * 2.0 * window.std() * np.sqrt(horizon))
