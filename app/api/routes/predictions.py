"""Prediction endpoints — runs the real agent swarm synchronously."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.agents.supervisor import SupervisorAgent
from app.api.deps import SessionDep
from app.db.repositories import PredictionRepository
from app.domain.prediction import PredictionRequest
from app.services.market.symbols import normalize_asset

router = APIRouter(prefix="/predictions", tags=["predictions"])

supervisor = SupervisorAgent()
repo = PredictionRepository()


@router.post("")
async def create_prediction(payload: PredictionRequest, session: SessionDep):
    asset = normalize_asset(payload.asset)
    try:
        result = await supervisor.run_workflow(
            asset, interval=payload.interval, horizon_bars=payload.horizon_bars, session=session
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, f"Agent workflow failed: {exc}") from exc

    if result.get("status") != "completed":
        raise HTTPException(502, result.get("error", "Agent workflow failed"))
    return result


@router.get("")
async def list_predictions(session: SessionDep, asset: str | None = None, limit: int = 50):
    records = await repo.list_recent(session, asset=asset, limit=min(limit, 200))
    return [_record_to_json(r) for r in records]


@router.get("/{prediction_id}")
async def get_prediction(prediction_id: str, session: SessionDep):
    record = await repo.get(session, prediction_id)
    if record is None:
        raise HTTPException(404, "Prediction not found")
    return _record_to_json(record)


def _record_to_json(r) -> dict:
    return {
        "id": str(r.id),
        "asset": r.asset,
        "interval": r.interval,
        "direction": r.direction,
        "probability": r.probability,
        "expected_return": r.expected_return,
        "expected_price": r.expected_price,
        "target_price": r.target_price,
        "stop_loss": r.stop_loss,
        "confidence_lower": r.confidence_lower,
        "confidence_upper": r.confidence_upper,
        "model_ensemble": r.model_ensemble,
        "kelly_size": r.kelly_size,
        "expected_value": r.expected_value,
        "risk_score": r.risk_score,
        "var_95": r.var_95,
        "sharpe_ratio": r.sharpe_ratio,
        "sortino_ratio": r.sortino_ratio,
        "max_drawdown": r.max_drawdown,
        "fused_probability": r.fused_probability,
        "fusion_weights": r.fusion_weights,
        "technical_probability": r.technical_probability,
        "consensus_probability": r.consensus_probability,
        "sentiment_score": r.sentiment_score,
        "market_regime": r.market_regime,
        "model_predictions": r.model_predictions,
        "rationale": r.rationale,
        "llm_summary": r.llm_summary,
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
