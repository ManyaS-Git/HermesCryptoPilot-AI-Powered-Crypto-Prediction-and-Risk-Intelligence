"""Data access layer for domain records."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AgentRun,
    NewsArticle,
    PredictionRecord,
    SentimentRecord,
    SignalFusionRecord,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PredictionRepository:
    @staticmethod
    async def create(session: AsyncSession, data: dict[str, Any]) -> PredictionRecord:
        record = PredictionRecord(**data)
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record

    @staticmethod
    async def get(session: AsyncSession, record_id: str) -> PredictionRecord | None:
        return await session.get(PredictionRecord, record_id)

    @staticmethod
    async def list_recent(
        session: AsyncSession, asset: str | None = None, limit: int = 50
    ) -> list[PredictionRecord]:
        stmt = select(PredictionRecord).order_by(PredictionRecord.created_at.desc())
        if asset:
            stmt = stmt.where(PredictionRecord.asset == asset.upper())
        stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars())

    @staticmethod
    async def calibration_history(
        session: AsyncSession, asset: str | None = None, days: int = 30
    ) -> tuple[list[float], list[int]]:
        """Return (probabilities, outcomes) from evaluated predictions."""
        since = _now() - timedelta(days=days)
        stmt = select(PredictionRecord).where(
            PredictionRecord.evaluated.is_(True),
            PredictionRecord.created_at >= since,
        )
        if asset:
            stmt = stmt.where(PredictionRecord.asset == asset.upper())
        result = await session.execute(stmt)
        records = list(result.scalars())
        probs: list[float] = []
        outcomes: list[int] = []
        for r in records:
            if r.probability is None:
                continue
            outcome = getattr(r, "_actual_outcome", None)
            if outcome is None:
                continue
            probs.append(r.probability)
            outcomes.append(outcome)
        return probs, outcomes


class AgentRunRepository:
    @staticmethod
    async def start(session: AsyncSession, agent_name: str, asset: str) -> AgentRun:
        run = AgentRun(agent_name=agent_name, asset=asset.upper(), status="running")
        session.add(run)
        await session.commit()
        await session.refresh(run)
        return run

    @staticmethod
    async def complete(
        session: AsyncSession,
        run: AgentRun,
        execution_time_ms: float,
        output: dict[str, Any] | None = None,
    ) -> None:
        run.status = "completed"
        run.execution_time_ms = execution_time_ms
        if output:
            run.output_json = _json_safe(output)
        await session.commit()

    @staticmethod
    async def fail(session: AsyncSession, run: AgentRun, error: str) -> None:
        run.status = "failed"
        run.error_message = error[:1000]
        await session.commit()

    @staticmethod
    async def list_runs(session: AsyncSession, limit: int = 100) -> list[AgentRun]:
        stmt = select(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars())


class NewsRepository:
    @staticmethod
    async def upsert(session: AsyncSession, articles: list[dict[str, Any]]) -> int:
        inserted = 0
        for article in articles:
            existing = await session.execute(
                select(NewsArticle).where(NewsArticle.url == article["url"])
            )
            if existing.scalar_one_or_none():
                continue
            session.add(NewsArticle(**article))
            inserted += 1
        if inserted:
            await session.commit()
        return inserted


class SentimentRepository:
    @staticmethod
    async def store(session: AsyncSession, data: dict[str, Any]) -> None:
        session.add(SentimentRecord(**data))
        await session.commit()


class FusionRepository:
    @staticmethod
    async def store(session: AsyncSession, data: dict[str, Any]) -> None:
        session.add(SignalFusionRecord(**data))
        await session.commit()


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return json.loads(json.dumps(value, default=str))
