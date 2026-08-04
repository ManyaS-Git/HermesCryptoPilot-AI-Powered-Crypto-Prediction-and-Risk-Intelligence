"""Risk engine: combines risk metrics, Monte Carlo, and Kelly sizing into a
concrete position recommendation."""
from __future__ import annotations

import numpy as np

from app.core.config import get_settings
from app.domain.fusion import SignalFusionResult
from app.domain.market import Candle
from app.domain.risk import PositionRecommendation, RiskMetrics, RiskParameters
from app.services.indicators.compute import candles_to_frame
from app.services.risk import metrics as M
from app.services.risk import montecarlo


class RiskEngine:
    def __init__(self, params: RiskParameters | None = None) -> None:
        settings = get_settings()
        self.params = params or RiskParameters(
            capital=10_000.0,
            kelly_fraction=settings.KELLY_FRACTION,
            max_position_size=settings.MAX_POSITION_SIZE,
            risk_free_rate=settings.RISK_FREE_RATE,
            var_confidence=settings.VAR_CONFIDENCE,
            monte_carlo_sims=settings.MONTE_CARLO_SIMS,
            monte_carlo_horizon=settings.MONTE_CARLO_HORIZON,
        )

    async def compute_metrics(self, candles: list[Candle], interval: str) -> RiskMetrics:
        df = candles_to_frame(candles)
        prices = df["close"].to_numpy()
        returns = M.log_returns(prices)

        var95 = M.value_at_risk(returns, self.params.var_confidence)
        cvar95 = M.conditional_var(returns, self.params.var_confidence)
        vol = M.annualized_volatility(returns, interval)
        sharpe = M.sharpe_ratio(returns, self.params.risk_free_rate, interval)
        sortino = M.sortino_ratio(returns, self.params.risk_free_rate, interval)
        mdd = M.max_drawdown(prices)

        mc = montecarlo.monte_carlo_simulate(
            prices,
            horizon_bars=self.params.monte_carlo_horizon,
            n_sims=self.params.monte_carlo_sims,
        )

        return RiskMetrics(
            var_95=round(var95, 6),
            cvar_95=round(cvar95, 6),
            volatility_annualized=round(vol, 6),
            sharpe_ratio=round(sharpe, 4),
            sortino_ratio=round(sortino, 4),
            max_drawdown=round(mdd, 6),
            monte_carlo_var_95=round(mc["var_95"], 6) if mc else None,
            monte_carlo_mean_return=round(mc["mean_return"], 6) if mc else None,
            monte_carlo_win_probability=round(mc["win_probability"], 4) if mc else None,
            kelly_fraction=0.0,
            expected_value=0.0,
        )

    async def recommend(
        self,
        fusion: SignalFusionResult,
        candles: list[Candle],
        interval: str,
    ) -> tuple[PositionRecommendation, RiskMetrics]:
        metrics = await self.compute_metrics(candles, interval)
        last_close = float(candles_to_frame(candles)["close"].iloc[-1])

        # Probability of the chosen direction
        if fusion.direction == "UP":
            win_prob = fusion.fused_probability
        else:
            win_prob = 1.0 - fusion.fused_probability

        # Net odds of 1:1 binary outcome; Kelly criterion
        b = 1.0
        kelly = M.kelly_fraction(win_prob, b)
        expected_value = win_prob * b - (1 - win_prob)

        # Apply fractional Kelly + cap
        kelly_sized = kelly * self.params.kelly_fraction
        kelly_sized = min(kelly_sized, self.params.max_position_size)
        position_value = self.params.capital * kelly_sized

        # Risk score from volatility + drawdown + VaR
        vol_component = min(1.0, metrics.volatility_annualized / 2.0)
        mdd_component = min(1.0, abs(metrics.max_drawdown) * 2.0)
        risk_score = round(0.6 * vol_component + 0.4 * mdd_component, 4)

        # Stop-loss / take-profit based on ATR
        atr_pct = M.volatility_regime_weight(metrics.volatility_annualized)
        buffer = 0.5 + atr_pct * 2.0
        stop_dist = 0.02 * buffer
        take_dist = 0.06 * buffer
        if fusion.direction == "UP":
            stop_loss = last_close * (1 - stop_dist)
            take_profit = last_close * (1 + take_dist)
        else:
            stop_loss = last_close * (1 + stop_dist)
            take_profit = last_close * (1 - take_dist)

        rec = PositionRecommendation(
            asset=fusion.asset,
            interval=interval,
            direction=fusion.direction,
            expected_value=round(expected_value, 6),
            kelly_size=round(kelly_sized, 4),
            suggested_position=round(position_value, 2),
            stop_loss=round(float(stop_loss), 6),
            take_profit=round(float(take_profit), 6),
            risk_score=risk_score,
            risk_level=M.risk_level(risk_score),
            rationale=(
                f"{fusion.direction} with fused probability {fusion.fused_probability:.2f}. "
                f"Kelly fraction {kelly_sized:.4f} -> ${position_value:,.2f}. "
                f"VaR(95%) {metrics.var_95:.2%}, max drawdown {metrics.max_drawdown:.2%}."
            ),
        )
        metrics.kelly_fraction = round(kelly_sized, 4)
        metrics.expected_value = round(expected_value, 6)
        return rec, metrics
