"""Feature engineering for the prediction ensemble.

Builds a supervised dataset from historical candles: features are technical
moments and regime signals; labels are future price directions/returns.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.indicators import compute

_FEATURE_COLUMNS: list[str] = []


def _log_feature(col: str) -> str:
    _FEATURE_COLUMNS.append(col)
    return col


def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Return a feature DataFrame aligned with the input candles."""
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"].astype(float)

    out = pd.DataFrame(index=df.index)

    # Price transforms
    out[_log_feature("log_return_1")] = np.log(close / close.shift(1))
    for lag in (3, 5, 10, 20):
        out[_log_feature(f"return_{lag}")] = close / close.shift(lag) - 1.0
        out[_log_feature(f"vol_return_{lag}")] = volume.pct_change(lag)
    out[_log_feature("return_60")] = close / close.shift(60) - 1.0

    # Position within recent range
    window_high = high.rolling(20).max()
    window_low = low.rolling(20).min()
    rng = (window_high - window_low).replace(0, np.nan)
    out[_log_feature("position_20")] = (close - window_low) / rng
    out[_log_feature("range_20")] = rng / close

    # Indicators
    out[_log_feature("rsi_14")] = compute.rsi(close)
    out[_log_feature("rsi_7")] = compute.rsi(close, 7)
    _, _, macd_hist = compute.macd(close)
    out[_log_feature("macd_hist")] = macd_hist
    out[_log_feature("macd_hist_norm")] = macd_hist / close
    mid, upper, lower, bandwidth = compute.bollinger(close)
    out[_log_feature("bollinger_bw")] = bandwidth
    out[_log_feature("bollinger_pctb")] = (close - lower) / (upper - lower).replace(0, np.nan)
    out[_log_feature("atr_pct")] = compute.atr(high, low, close) / close
    out[_log_feature("adx_14")] = compute.adx(high, low, close)
    out[_log_feature("obv_slope")] = compute.obv(close, volume).pct_change(10)
    vwap_series = compute.vwap(df)
    out[_log_feature("vwap_dist")] = (close / vwap_series - 1.0)
    out[_log_feature("ema_ratio")] = compute.ema(close, 12) / compute.ema(close, 26).replace(0, np.nan)
    out[_log_feature("sma_ratio")] = compute.sma(close, 50) / compute.sma(close, 200).replace(0, np.nan)
    st = compute.supertrend(df)
    out[_log_feature("supertrend_pos")] = (st < close).astype(float)

    # Volume z-score
    vol_mean = volume.rolling(20).mean()
    vol_std = volume.rolling(20).std().replace(0, np.nan)
    out[_log_feature("volume_z")] = (volume - vol_mean) / vol_std

    # Volatility
    out[_log_feature("realized_vol_20")] = out["log_return_1"].rolling(20).std() * np.sqrt(20)

    # Session features
    if len(df) and "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], utc=True)
        out[_log_feature("hour")] = ts.dt.hour / 23.0
        out[_log_feature("dow")] = ts.dt.dayofweek / 6.0

    # Drop rows with any NaN (burn-in period)
    out = out.replace([np.inf, -np.inf], np.nan)
    return out.dropna()


def create_labels(df: pd.DataFrame, horizon: int = 1) -> pd.Series:
    """Label each bar with the future log-return over ``horizon`` bars."""
    close = df["close"]
    future = close.shift(-horizon)
    return np.log(future / close).replace([np.inf, -np.inf], np.nan)


def build_training_frame(df: pd.DataFrame, horizon: int = 1) -> tuple[pd.DataFrame, pd.Series]:
    features = build_feature_frame(df)
    labels = create_labels(df, horizon)
    aligned = pd.concat([features, labels.rename("future_return")], axis=1)
    aligned = aligned.dropna()
    X = aligned.drop(columns=["future_return"])
    y = aligned["future_return"]
    return X, y


def feature_columns() -> list[str]:
    if not _FEATURE_COLUMNS:
        # warm up with a tiny frame to discover columns
        sample = pd.DataFrame(
            {"open": [1.0] * 250, "high": [1.1] * 250, "low": [0.9] * 250,
             "close": [1.0] * 250, "volume": [100.0] * 250,
             "timestamp": pd.date_range("2024-01-01", periods=250, tz="UTC")}
        )
        build_feature_frame(sample)
    return list(_FEATURE_COLUMNS)
