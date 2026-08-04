"""Signal fusion with dynamic weighting.

Instead of fixed 60/40 weights, the blend of technical, consensus, and
sentiment signals is adjusted by:
- market regime / volatility (unreliable signals are downweighted)
- model conviction (distance of probabilities from 0.5)
- historical accuracy of the technical engine (from persisted evaluations)
- news sentiment (enters as an independent signal)
"""
from __future__ import annotations

import numpy as np

from app.domain.fusion import SignalFusionResult
from app.domain.intel import UnifiedMarketConsensus
from app.domain.news import SentimentResult
from app.domain.prediction import CalibratedPrediction
from app.services.market.symbols import normalize_asset


def _sigmoid_conviction(probability: float) -> float:
    """Map distance-from-0.5 to a 0..1 conviction weight."""
    return float(np.clip((abs(probability - 0.5) * 2.0) ** 1.5, 0.05, 1.0))


class SignalFusionEngine:
    def __init__(
        self,
        base_tech_weight: float = 0.5,
        base_consensus_weight: float = 0.3,
        base_sentiment_weight: float = 0.2,
    ) -> None:
        self.base_tech = base_tech_weight
        self.base_consensus = base_consensus_weight
        self.base_sentiment = base_sentiment_weight

    def fuse(
        self,
        technicals: CalibratedPrediction,
        consensus: UnifiedMarketConsensus,
        sentiment: SentimentResult | None,
        regime: dict,
        historical_accuracy: float | None = None,
    ) -> SignalFusionResult:
        asset = normalize_asset(technicals.asset)

        # Technical probability of UP
        tech_up = technicals.calibrated_probability
        if technicals.direction == "DOWN":
            tech_up = 1.0 - tech_up

        cons_up = consensus.consensus_probability
        sent_up = _sentiment_to_probability(sentiment)

        # Conviction weights
        tech_conviction = _sigmoid_conviction(tech_up)
        cons_conviction = _sigmoid_conviction(cons_up)

        # Volatility discount — high volatility reduces reliance on direction
        volatility = float(regime.get("volatility", 0.0) or 0.0)
        vol_discount = np.clip(1.0 - volatility / 6.0, 0.4, 1.0)

        # Historical accuracy boost for the technical engine
        accuracy_boost = 1.0
        if historical_accuracy is not None:
            accuracy_boost = float(np.clip(0.5 + historical_accuracy, 0.6, 1.2))

        tech_w = self.base_tech * tech_conviction * accuracy_boost * vol_discount
        cons_w = self.base_consensus * cons_conviction * vol_discount
        sent_w = self.base_sentiment

        # Normalise weights
        total = tech_w + cons_w + sent_w
        tech_w, cons_w, sent_w = tech_w / total, cons_w / total, sent_w / total

        fused = tech_w * tech_up + cons_w * cons_up + sent_w * sent_up
        fused = float(np.clip(fused, 0.01, 0.99))
        direction = "UP" if fused >= 0.5 else "DOWN"

        regime_label = regime.get("regime", "unknown")
        rationale = (
            f"Dynamic fusion in {regime_label} regime (vol {volatility:.2f}%). "
            f"Technical {tech_up:.2f} @ {tech_w:.2f}w, consensus {cons_up:.2f} @ {cons_w:.2f}w, "
            f"sentiment {sent_up:.2f} @ {sent_w:.2f}w. "
            f"Conviction: tech={tech_conviction:.2f}, consensus={cons_conviction:.2f}."
        )

        return SignalFusionResult(
            asset=asset,
            fused_probability=round(fused, 4),
            direction=direction,
            technical_probability=round(float(tech_up), 4),
            consensus_probability=round(float(cons_up), 4),
            sentiment_score=sentiment.score if sentiment else None,
            weights={
                "technical": round(float(tech_w), 4),
                "consensus": round(float(cons_w), 4),
                "sentiment": round(float(sent_w), 4),
            },
            market_regime=regime_label,
            rationale=rationale,
        )


def _sentiment_to_probability(sentiment: SentimentResult | None) -> float:
    if sentiment is None or sentiment.article_count == 0:
        return 0.5
    score = float(np.clip(sentiment.score, -1, 1))
    # Logistic map of sentiment score into probability space
    return float(1 / (1 + np.exp(-2.5 * score)))
