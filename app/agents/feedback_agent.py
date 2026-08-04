"""Feedback Agent: persists prediction outcomes to the database to build
calibration memory and enable historical evaluation."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import PredictionRepository


class FeedbackAgent:
    def __init__(self) -> None:
        self.repo = PredictionRepository()

    async def store_prediction(self, session: AsyncSession, data: dict) -> str:
        record = await self.repo.create(session, data)
        return str(record.id)
