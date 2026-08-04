"""Supervisor Agent: orchestrates the full agent swarm for a prediction.

Workflow (all real data, no mocks):
  1. MarketDataAgent + MarketIntelAgent  (concurrent)
  2. PredictionAgent  -> ensemble prediction
  3. EvaluationAgent  -> calibration with outcome history
  4. SentimentService -> news sentiment
  5. SignalFusionAgent -> dynamic-weight fusion
  6. RiskAgent        -> Kelly sizing + risk metrics
  7. LLMService       -> executive rationale
  8. FeedbackAgent    -> persist prediction + agent telemetry

Each agent's execution time is recorded and persisted as an AgentRun.
"""
from __future__ import annotations

import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.data_agent import MarketDataAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.feedback_agent import FeedbackAgent
from app.agents.market_intel import MarketIntelAgent
from app.agents.prediction_agent import PredictionAgent
from app.agents.risk_agent import RiskAgent
from app.agents.signal_fusion import SignalFusionAgent
from app.db.repositories import AgentRunRepository, PredictionRepository
from app.services.intelligence.sentiment import SentimentService
from app.services.llm.service import LLMService
from app.services.market.symbols import normalize_asset


class SupervisorAgent:
    def __init__(self) -> None:
        self.data_agent = MarketDataAgent()
        self.intel_agent = MarketIntelAgent()
        self.prediction_agent = PredictionAgent()
        self.evaluation_agent = EvaluationAgent()
        self.sentiment_service = SentimentService()
        self.fusion_agent = SignalFusionAgent()
        self.risk_agent = RiskAgent()
        self.feedback_agent = FeedbackAgent()
        self.llm = LLMService()
        self.repo = PredictionRepository()
        self.run_repo = AgentRunRepository()

    async def run_workflow(
        self,
        asset: str,
        interval: str = "15m",
        horizon_bars: int = 1,
        session: AsyncSession | None = None,
    ) -> dict[str, Any]:
        asset = normalize_asset(asset)
        timings: dict[str, float] = {}
        statuses: dict[str, str] = {}
        result: dict[str, Any] = {
            "asset": asset,
            "interval": interval,
            "horizon_bars": horizon_bars,
        }

        # --- Agent 1 & 2: data + intel (concurrent) ---
        statuses["MarketDataAgent"] = "running"
        statuses["MarketIntelAgent"] = "running"
        start = time.perf_counter()
        data_task = self.data_agent.fetch_historical_data(
            asset, timeframes=[interval, "1h"], limit=500
        )
        intel_task = self.intel_agent.get_market_consensus(asset)
        data_dict, intel = await _gather(data_task, intel_task)
        timings["MarketDataAgent"] = (time.perf_counter() - start) * 1000
        statuses["MarketDataAgent"] = "completed" if data_dict else "failed"

        candles = data_dict.get(interval) or data_dict.get("1h")
        if not candles:
            result.update(
                status="failed",
                error="Market data agent could not retrieve historical candles.",
                timings=timings,
                agent_statuses=statuses,
            )
            return result
        timings["MarketIntelAgent"] = (time.perf_counter() - start) * 1000
        statuses["MarketIntelAgent"] = "completed"

        indicators = await self.data_agent.get_indicators(asset, interval)
        regime = indicators.get("regime", {})

        # --- Agent 3: prediction ---
        statuses["PredictionAgent"] = "running"
        start = time.perf_counter()
        history_probs, history_outcomes = await self._calibration_history(session, asset)
        prediction = await self.prediction_agent.run_prediction(
            asset,
            candles,
            interval=interval,
            horizon_bars=horizon_bars,
            history_probs=history_probs,
            history_outcomes=history_outcomes,
        )
        timings["PredictionAgent"] = (time.perf_counter() - start) * 1000
        statuses["PredictionAgent"] = "completed"

        # --- Agent 4: evaluation / calibration ---
        statuses["EvaluationAgent"] = "running"
        start = time.perf_counter()
        calibrated = await self.evaluation_agent.calibrate(
            prediction, history_probs, history_outcomes
        )
        timings["EvaluationAgent"] = (time.perf_counter() - start) * 1000
        statuses["EvaluationAgent"] = "completed"

        # --- Sentiment intelligence ---
        statuses["SentimentAgent"] = "running"
        start = time.perf_counter()
        sentiment = None
        try:
            sentiment = await self.sentiment_service.analyze(asset)
        except Exception:
            sentiment = None
        timings["SentimentAgent"] = (time.perf_counter() - start) * 1000
        statuses["SentimentAgent"] = "completed"

        # --- Agent 5: signal fusion ---
        statuses["SignalFusionAgent"] = "running"
        start = time.perf_counter()
        fusion = await self.fusion_agent.fuse_signals(
            calibrated,
            intel.consensus,
            sentiment=sentiment,
            regime=regime,
            historical_accuracy=None,
        )
        timings["SignalFusionAgent"] = (time.perf_counter() - start) * 1000
        statuses["SignalFusionAgent"] = "completed"

        # --- Agent 6: risk / Kelly ---
        statuses["RiskAgent"] = "running"
        start = time.perf_counter()
        recommendation, risk_metrics = await self.risk_agent.calculate_kelly_size(
            fusion, candles, interval=interval
        )
        timings["RiskAgent"] = (time.perf_counter() - start) * 1000
        statuses["RiskAgent"] = "completed"

        # --- LLM reasoning ---
        statuses["LLMReasoningAgent"] = "running"
        start = time.perf_counter()
        summary_payload = (
            f"Asset: {asset} ({interval})\n"
            f"Technical probability: {calibrated.calibrated_probability:.2f} ({calibrated.direction})\n"
            f"Market consensus: {intel.consensus.consensus_probability:.2f}\n"
            f"News sentiment: {sentiment.label if sentiment else 'n/a'} ({sentiment.score if sentiment else 0:+.2f})\n"
            f"Fused probability: {fusion.fused_probability:.2f}\n"
            f"Expected return: {prediction.expected_return:+.2%}\n"
            f"Risk: VaR(95%) {risk_metrics.var_95:.2%}, max DD {risk_metrics.max_drawdown:.2%}, "
            f"Sharpe {risk_metrics.sharpe_ratio:.2f}\n"
            f"Recommended position: ${recommendation.suggested_position:,.2f} "
            f"(Kelly {recommendation.kelly_size:.4f}) with stop at {recommendation.stop_loss}."
        )
        llm_summary = await self.llm.explain_signal(summary_payload)
        timings["LLMReasoningAgent"] = (time.perf_counter() - start) * 1000
        statuses["LLMReasoningAgent"] = "completed"

        # --- Agent 8: feedback / memory ---
        statuses["FeedbackAgent"] = "running"
        start = time.perf_counter()
        prediction_id = None
        if session is not None:
            prediction_id = await self.feedback_agent.store_prediction(
                session,
                _prediction_payload(
                    asset, interval, horizon_bars, prediction, calibrated, fusion,
                    recommendation, risk_metrics, sentiment, regime, llm_summary,
                ),
            )
            await self._persist_runs(session, asset, statuses, timings)
        timings["FeedbackAgent"] = (time.perf_counter() - start) * 1000
        statuses["FeedbackAgent"] = "completed"

        result.update(
            status="completed",
            prediction_id=prediction_id,
            prediction=prediction.model_dump(),
            calibrated=calibrated.model_dump(),
            fusion=fusion.model_dump(),
            recommendation=recommendation.model_dump(),
            risk_metrics=risk_metrics.model_dump(),
            sentiment=sentiment.model_dump() if sentiment else None,
            market_intel=intel.model_dump(),
            indicators={
                "latest": indicators.get("latest"),
                "regime": regime,
                "last_close": indicators.get("last_close"),
            },
            llm_summary=llm_summary,
            timings=timings,
            agent_statuses=statuses,
        )
        return result

    async def _calibration_history(
        self, session: AsyncSession | None, asset: str
    ) -> tuple[list[float], list[int]]:
        if session is None:
            return [], []
        return await self.repo.calibration_history(session, asset=asset, days=45)

    async def _persist_runs(
        self, session: AsyncSession, asset: str, statuses: dict, timings: dict
    ) -> None:
        for name, status in statuses.items():
            run = await self.run_repo.start(session, name, asset)
            if status == "completed":
                await self.run_repo.complete(
                    session, run, timings.get(name, 0.0)
                )
            elif status == "failed":
                await self.run_repo.fail(session, run, "agent failed")


def _prediction_payload(
    asset, interval, horizon_bars, prediction, calibrated, fusion,
    recommendation, risk_metrics, sentiment, regime, llm_summary,
) -> dict[str, Any]:
    return {
        "asset": asset,
        "interval": interval,
        "horizon_bars": horizon_bars,
        "direction": prediction.direction,
        "probability": prediction.probability,
        "expected_return": prediction.expected_return,
        "expected_price": prediction.expected_price,
        "target_price": recommendation.take_profit,
        "stop_loss": recommendation.stop_loss,
        "confidence_lower": prediction.confidence_lower,
        "confidence_upper": prediction.confidence_upper,
        "model_ensemble": ",".join(sorted(prediction.model_weights.keys())),
        "signal_direction": recommendation.direction,
        "kelly_size": recommendation.kelly_size,
        "expected_value": recommendation.expected_value,
        "risk_score": recommendation.risk_score,
        "var_95": risk_metrics.var_95,
        "sharpe_ratio": risk_metrics.sharpe_ratio,
        "sortino_ratio": risk_metrics.sortino_ratio,
        "max_drawdown": risk_metrics.max_drawdown,
        "fused_probability": fusion.fused_probability,
        "fusion_weights": fusion.weights,
        "technical_probability": calibrated.calibrated_probability,
        "consensus_probability": fusion.consensus_probability,
        "sentiment_score": sentiment.score if sentiment else None,
        "market_regime": regime.get("regime", "unknown"),
        "model_predictions": [m.model_dump() for m in prediction.model_predictions],
        "indicators": {},
        "rationale": recommendation.rationale,
        "llm_summary": llm_summary,
        "status": "completed",
    }


async def _gather(*tasks):
    import asyncio

    results = await asyncio.gather(*tasks, return_exceptions=True)
    out = []
    for r in results:
        if isinstance(r, Exception):
            out.append(None)
        else:
            out.append(r)
    return out
