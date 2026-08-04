"""Monte Carlo simulation of horizon returns using real historical drift
and volatility — geometric Brownian motion calibrated to observed data."""
from __future__ import annotations

import numpy as np


def monte_carlo_simulate(
    prices: np.ndarray,
    horizon_bars: int = 24,
    n_sims: int = 10_000,
    seed: int = 42,
) -> dict[str, float]:
    """Simulate the distribution of cumulative return over ``horizon_bars``.

    Calibration inputs are computed from actual prices:
    - ``mu``: annualised drift from log returns
    - ``sigma``: per-bar volatility
    """
    prices = np.asarray(prices, dtype=float)
    prices = prices[prices > 0]
    if len(prices) < 30:
        return {}

    log_r = np.diff(np.log(prices))
    if len(log_r) < 5 or np.std(log_r) == 0:
        return {}

    mu_bar = float(np.mean(log_r))
    sigma_bar = float(np.std(log_r, ddof=1))
    if sigma_bar == 0:
        return {}

    rng = np.random.default_rng(seed)
    dt = 1.0
    increments = (mu_bar - 0.5 * sigma_bar ** 2) * dt + sigma_bar * rng.standard_normal(
        (n_sims, horizon_bars)
    )
    cumulative = np.cumsum(increments, axis=1)[:, -1]

    return {
        "mean_return": float(np.mean(cumulative)),
        "var_95": float(-np.quantile(cumulative, 0.05)),
        "var_99": float(-np.quantile(cumulative, 0.01)),
        "win_probability": float(np.mean(cumulative > 0)),
        "median_return": float(np.median(cumulative)),
        "best_5": float(np.quantile(cumulative, 0.95)),
        "worst_5": float(np.quantile(cumulative, 0.05)),
    }
