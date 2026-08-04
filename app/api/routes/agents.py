"""Agent status and telemetry endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.db.repositories import AgentRunRepository

router = APIRouter(prefix="/agents", tags=["agents"])

run_repo = AgentRunRepository()

AGENT_REGISTRY = [
    {"id": "supervisor", "name": "SupervisorAgent", "role": "Orchestrator"},
    {"id": "data", "name": "MarketDataAgent", "role": "Market Data"},
    {"id": "intel", "name": "MarketIntelAgent", "role": "Market Intelligence"},
    {"id": "prediction", "name": "PredictionAgent", "role": "Prediction Engine"},
    {"id": "evaluation", "name": "EvaluationAgent", "role": "Calibration"},
    {"id": "sentiment", "name": "SentimentAgent", "role": "Sentiment Intelligence"},
    {"id": "fusion", "name": "SignalFusionAgent", "role": "Signal Fusion"},
    {"id": "risk", "name": "RiskAgent", "role": "Position Sizing & Risk"},
    {"id": "llm", "name": "LLMReasoningAgent", "role": "AI Reasoning"},
    {"id": "feedback", "name": "FeedbackAgent", "role": "Memory & Feedback"},
]


@router.get("")
async def list_agents(session: SessionDep):
    """Registry enriched with latest real execution telemetry."""
    runs = await run_repo.list_runs(session, limit=200)
    status_by_name: dict[str, dict] = {}
    for run in runs:
        current = status_by_name.get(run.agent_name)
        if current is None or run.created_at > current.get("created_at"):
            status_by_name[run.agent_name] = {
                "status": run.status,
                "last_run": run.created_at.isoformat() if run.created_at else None,
                "execution_time_ms": run.execution_time_ms,
                "asset": run.asset,
                "error": run.error_message,
            }
    return [
        {
            **agent,
            "status": (status_by_name.get(agent["name"]) or {}).get("status", "idle"),
            "last_run": (status_by_name.get(agent["name"]) or {}).get("last_run"),
            "execution_time_ms": (status_by_name.get(agent["name"]) or {}).get("execution_time_ms"),
            "last_asset": (status_by_name.get(agent["name"]) or {}).get("asset"),
        }
        for agent in AGENT_REGISTRY
    ]


@router.get("/runs")
async def recent_runs(session: SessionDep, limit: int = 50):
    runs = await run_repo.list_runs(session, limit=min(limit, 200))
    return [
        {
            "id": str(r.id),
            "agent_name": r.agent_name,
            "asset": r.asset,
            "status": r.status,
            "execution_time_ms": r.execution_time_ms,
            "error": r.error_message,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]
