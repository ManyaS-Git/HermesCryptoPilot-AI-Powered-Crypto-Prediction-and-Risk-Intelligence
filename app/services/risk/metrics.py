"""Risk metrics computed from real returns.

Implements value-at-risk, CVaR, Sharpe/Sortino ratios, maximum drawdown,
Kelly position sizing, and portfolio analytics. All calculations use
historical returns — no synthetic or fabricated inputs.
"""
from __future__ import annotations

import numpy as np

from app.core.config import get_settings

TRADING_DAYS = 365
BARS_PER_YEAR = {"1m": 525_600, "5m": 105_120, "15m": 35_040, "30m": 17_520,
                 "1h": 8_760, "4h": 2_190, "1d": 365, "1w": 52}


def log_returns(prices: np.ndarray) -> np.ndarray:
    prices = np.asarray(prices, dtype=float)
    prices = prices[prices > 0]
    if len(prices) < 2:
        return np.array([])
    return np.diff(np.log(prices))


def annualized_volatility(returns: np.ndarray, interval: str = "15m") -> float:
    if len(returns) < 2:
        return 0.0
    bars = BARS_PER_YEAR.get(interval, 35_040)
    return float(np.std(returns, ddof=1) * np.sqrt(bars))


def value_at_risk(returns: np.ndarray, confidence: float = 0.95) -> float:
    """Historical VaR: the loss threshold at the given confidence level."""
    if len(returns) < 2:
        return 0.0
    return float(-np.quantile(returns, 1 - confidence))


def conditional_var(returns: np.ndarray, confidence: float = 0.95) -> float:
    """Expected shortfall (CVaR): average loss beyond the VaR threshold."""
    if len(returns) < 2:
        return 0.0
    threshold = np.quantile(returns, 1 - confidence)
    tail = returns[returns <= threshold]
    if len(tail) == 0:
        return float(-threshold)
    return float(-np.mean(tail))


def sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02, interval: str = "15m") -> float:
    if len(returns) < 2:
        return 0.0
    bars = BARS_PER_YEAR.get(interval, 35_040)
    rf_per_bar = risk_free_rate / bars
    excess = returns - rf_per_bar
    std = np.std(excess, ddof=1)
    if std == 0:
        return 0.0
    return float(np.mean(excess) / std * np.sqrt(bars))


def sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.02, interval: str = "15m") -> float:
    if len(returns) < 2:
        return 0.0
    bars = BARS_PER_YEAR.get(interval, 35_040)
    rf_per_bar = risk_free_rate / bars
    excess = returns - rf_per_bar
    downside = excess[excess < 0]
    if len(downside) == 0 or np.std(downside, ddof=1) == 0:
        return 0.0
    return float(np.mean(excess) / np.std(downside, ddof=1) * np.sqrt(bars))


def max_drawdown(prices: np.ndarray) -> float:
    prices = np.asarray(prices, dtype=float)
    if len(prices) < 2:
        return 0.0
    running_max = np.maximum.accumulate(prices)
    drawdown = prices / running_max - 1.0
    return float(np.min(drawdown))


def kelly_fraction(probability: float, b: float = 1.0) -> float:
    """Full-Kelly fraction for a binary bet with net odds ``b``."""
    if b <= 0:
        return 0.0
    p = float(np.clip(probability, 0.0, 1.0))
    expected_value = p * b - (1 - p)
    if expected_value <= 0:
        return 0.0
    return float(((p * (b + 1.0)) - 1.0) / b)


def correlation_matrix(returns_by_asset: dict[str, np.ndarray]) -> dict[str, dict[str, float]]:
    """Pairwise Pearson correlation of daily (aligned) returns."""
    assets = list(returns_by_asset.keys())
    matrix: dict[str, dict[str, float]] = {a: {} for a in assets}
    for i, a in enumerate(assets):
        for j, b in enumerate(assets):
            ra = returns_by_asset[a]
            rb = returns_by_asset[b]
            n = min(len(ra), len(rb))
            if n < 2:
                matrix[a][b] = 0.0
                continue
            x = ra[-n:]
            y = rb[-n:]
            std_x = np.std(x)
            std_y = np.std(y)
            if std_x == 0 or std_y == 0:
                corr = 0.0
            else:
                corr = float(np.corrcoef(x, y)[0, 1])
            matrix[a][b] = round(corr, 4) if np.isfinite(corr) else 0.0
    return matrix


def diversification_score(allocation: dict[str, float], correlation: dict[str, dict[str, float]]) -> float:
    """Score 0..1 reflecting how diversified a portfolio is.

    Combines concentration (Herfindahl index) and average cross-correlation.
    """
    weights = np.array([v for v in allocation.values() if v > 0], dtype=float)
    if len(weights) == 0:
        return 0.0
    weights = weights / weights.sum()
    hhi = float(np.sum(weights ** 2))
    count_component = min(1.0, len(weights) / 5.0)

    assets = list(allocation.keys())
    corrs = []
    for i, a in enumerate(assets):
        for j, b in enumerate(assets):
            if i < j:
                corrs.append(correlation.get(a, {}).get(b, 0.0))
    avg_corr = float(np.mean(corrs)) if corrs else 0.0
    correlation_component = 1.0 - max(0.0, min(1.0, avg_corr))

    return round(0.5 * (1 - hhi) + 0.25 * count_component + 0.25 * correlation_component, 4)


def risk_level(score: float) -> str:
    if score < 0.3:
        return "low"
    if score < 0.6:
        return "medium"
    return "high"


def volatility_regime_weight(atr_pct: float) -> float:
    """Dynamic reliability weight: lower weight to directional signals in
    high-volatility regimes."""
    return float(np.clip(1.0 - atr_pct / 6.0, 0.3, 1.0))
