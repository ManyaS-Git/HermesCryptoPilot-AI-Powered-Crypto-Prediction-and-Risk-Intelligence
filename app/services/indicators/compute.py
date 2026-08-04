"""Technical indicators computed from real OHLCV data.

All functions are pure pandas/numpy implementations — no external TA libs.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.domain.market import Candle


def candles_to_frame(candles: list[Candle]) -> pd.DataFrame:
    df = pd.DataFrame([c.model_dump() for c in candles])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(period, min_periods=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50.0)


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger(close: pd.Series, period: int = 20, num_std: float = 2.0):
    mid = sma(close, period)
    std = close.rolling(period, min_periods=period).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    bandwidth = (upper - lower) / mid.replace(0, np.nan)
    return mid, upper, lower, bandwidth


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    return true_range(high, low, close).ewm(alpha=1 / period, adjust=False).mean()


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()


def vwap(df: pd.DataFrame) -> pd.Series:
    typical = (df["high"] + df["low"] + df["close"]) / 3
    cum_pv = (typical * df["volume"]).cumsum()
    cum_v = df["volume"].cumsum()
    return cum_pv / cum_v.replace(0, np.nan)


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    tr = true_range(high, low, close)
    tr_s = tr.ewm(alpha=1 / period, adjust=False).mean().replace(0, np.nan)
    plus_di = 100 * pd.Series(plus_dm).ewm(alpha=1 / period, adjust=False).mean() / tr_s
    minus_di = 100 * pd.Series(minus_dm).ewm(alpha=1 / period, adjust=False).mean() / tr_s
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / period, adjust=False).mean().fillna(0)


def ichimoku(df: pd.DataFrame, tenkan: int = 9, kijun: int = 26, senkou: int = 52):
    def midpoint(period: int) -> pd.Series:
        high = df["high"].rolling(period, min_periods=1).max()
        low = df["low"].rolling(period, min_periods=1).min()
        return (high + low) / 2

    tenkan_sen = midpoint(tenkan)
    kijun_sen = midpoint(kijun)
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
    senkou_span_b = midpoint(senkou).shift(kijun)
    chikou_span = df["close"].shift(-kijun)
    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span


def fibonacci_levels(high: pd.Series, low: pd.Series, lookback: int = 100) -> dict[str, float]:
    window_high = high.rolling(lookback, min_periods=10).max().iloc[-1]
    window_low = low.rolling(lookback, min_periods=10).min().iloc[-1]
    diff = window_high - window_low
    if not diff or np.isnan(diff):
        return {}
    levels = {
        "0.0": window_high,
        "0.236": window_high - 0.236 * diff,
        "0.382": window_high - 0.382 * diff,
        "0.5": window_high - 0.5 * diff,
        "0.618": window_high - 0.618 * diff,
        "0.786": window_high - 0.786 * diff,
        "1.0": window_low,
    }
    return levels


def supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.Series:
    close, high, low = df["close"], df["high"], df["low"]
    atr_val = atr(high, low, close, period)
    hl2 = (high + low) / 2
    upper_band = hl2 + multiplier * atr_val
    lower_band = hl2 - multiplier * atr_val

    final_upper = upper_band.copy()
    final_lower = lower_band.copy()
    st = pd.Series(np.nan, index=df.index)
    st.iloc[0] = lower_band.iloc[0]

    for i in range(1, len(df)):
        prev_close = close.iloc[i - 1]
        prev_upper = final_upper.iloc[i - 1]
        prev_lower = final_lower.iloc[i - 1]
        if not np.isnan(prev_upper) and not np.isnan(prev_lower):
            if upper_band.iloc[i] > prev_upper:
                final_upper.iloc[i] = prev_upper
            if lower_band.iloc[i] < prev_lower:
                final_lower.iloc[i] = prev_lower
        if prev_close <= final_upper.iloc[i]:
            st.iloc[i] = final_upper.iloc[i]
        else:
            st.iloc[i] = final_lower.iloc[i]

    return st


def compute_all(df: pd.DataFrame) -> dict[str, Any]:
    """Compute the full indicator set; returns latest values + recent series."""
    close = df["close"]
    latest: dict[str, Any] = {}
    series: dict[str, Any] = {}

    latest["sma_20"] = _last(sma(close, 20))
    latest["sma_50"] = _last(sma(close, 50))
    latest["sma_200"] = _last(sma(close, 200))
    latest["ema_12"] = _last(ema(close, 12))
    latest["ema_26"] = _last(ema(close, 26))
    latest["ema_50"] = _last(ema(close, 50))
    latest["rsi_14"] = _last(rsi(close))
    latest["rsi_7"] = _last(rsi(close, 7))
    macd_line, signal_line, hist = macd(close)
    latest["macd"] = _last(macd_line)
    latest["macd_signal"] = _last(signal_line)
    latest["macd_histogram"] = _last(hist)
    mid, upper, lower, bandwidth = bollinger(close)
    latest["bollinger_upper"] = _last(upper)
    latest["bollinger_lower"] = _last(lower)
    latest["bollinger_mid"] = _last(mid)
    latest["bollinger_bandwidth"] = _last(bandwidth)
    latest["atr_14"] = _last(atr(df["high"], df["low"], close))
    latest["atr_pct"] = _last(atr(df["high"], df["low"], close) / close.replace(0, np.nan) * 100)
    latest["obv"] = _last(obv(close, df["volume"]))
    latest["vwap"] = _last(vwap(df))
    latest["adx_14"] = _last(adx(df["high"], df["low"], close))
    latest["super_trend"] = _last(supertrend(df))
    latest["super_trend_signal"] = "buy" if latest["super_trend"] < close.iloc[-1] else "sell"

    tenkan, kijun, senkou_a, senkou_b, chikou = ichimoku(df)
    latest["ichimoku_tenkan"] = _last(tenkan)
    latest["ichimoku_kijun"] = _last(kijun)
    latest["ichimoku_senkou_a"] = _last(senkou_a)
    latest["ichimoku_senkou_b"] = _last(senkou_b)
    latest["ichimoku_cloud"] = _max(tenkan, kijun, senkou_a, senkou_b)

    latest["fibonacci"] = fibonacci_levels(df["high"], df["low"])

    # Series (trimmed) for charting
    recent = df["timestamp"].iloc[-120:].dt.strftime("%Y-%m-%dT%H:%M:%SZ").tolist()
    series["timestamps"] = recent
    series["close"] = [round(float(x), 6) for x in close.iloc[-120:]]
    series["rsi"] = [round(float(x), 2) for x in rsi(close).iloc[-120:]]
    series["macd"] = [round(float(x), 6) for x in macd_line.iloc[-120:]]
    series["macd_signal"] = [round(float(x), 6) for x in signal_line.iloc[-120:]]
    series["macd_histogram"] = [round(float(x), 6) for x in hist.iloc[-120:]]
    series["bollinger_upper"] = [round(float(x), 6) for x in upper.iloc[-120:]]
    series["bollinger_lower"] = [round(float(x), 6) for x in lower.iloc[-120:]]
    series["atr"] = [round(float(x), 6) for x in atr(df["high"], df["low"], close).iloc[-120:]]
    series["vwap"] = [round(float(x), 6) for x in vwap(df).iloc[-120:]]

    return {"latest": latest, "series": series}


def detect_regime(df: pd.DataFrame) -> dict[str, Any]:
    """Classify the current market regime using ADX and ATR."""
    close = df["close"]
    adx_val = _last(adx(df["high"], df["low"], close))
    atr_pct = _last(atr(df["high"], df["low"], close) / close.replace(0, np.nan) * 100)

    lookback = min(50, len(df) - 1)
    recent = close.iloc[-lookback:]
    if len(recent) > 5:
        change = (recent.iloc[-1] / recent.iloc[0]) - 1
        rolling_std = recent.pct_change().std() * np.sqrt(lookback)
    else:
        change = 0.0
        rolling_std = 0.0

    if atr_pct > 4.0 or rolling_std > 0.08:
        regime = "high_volatility"
    elif adx_val > 25 and change > 0:
        regime = "trending_up"
    elif adx_val > 25 and change < 0:
        regime = "trending_down"
    else:
        regime = "ranging"

    support = float(close.iloc[-20:].min()) if len(close) >= 20 else float(close.min())
    resistance = float(close.iloc[-20:].max()) if len(close) >= 20 else float(close.max())
    return {
        "regime": regime,
        "volatility": round(float(atr_pct or 0), 4),
        "trend_strength": round(float(adx_val or 0), 2),
        "adx": round(float(adx_val or 0), 2),
        "atr_pct": round(float(atr_pct or 0), 4),
        "support": support,
        "resistance": resistance,
        "recent_change_pct": round(float(change * 100), 3),
    }


def _last(s: pd.Series) -> Any:
    if s is None or len(s) == 0:
        return None
    val = s.iloc[-1]
    if isinstance(val, (np.integer, np.floating)):
        val = float(val)
    if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
        return None
    return val


def _max(*series: pd.Series) -> float | None:
    vals = [_last(s) for s in series]
    vals = [v for v in vals if v is not None]
    return max(vals) if vals else None
