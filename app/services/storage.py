"""Backward-compatible storage facade.

The original ``DatabaseManager`` wrote directly to aiosqlite. It now
delegates to the SQLAlchemy engine/session layer so that existing imports
(``from app.services.storage import DatabaseManager``) keep working while the
application uses a real ORM + Alembic migrations underneath.
"""
from __future__ import annotations

import logging

from app.db.base import Base
from app.db.session import engine, init_db

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_url: str | None = None) -> None:
        if db_url is not None:
            logger.info("db_url override provided; using default engine instead")
        self.engine = engine

    async def init_db(self) -> None:
        await init_db()

    async def create_all(self) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def execute_query(self, query: str, params: tuple = ()) -> list[dict]:
        """Raw query execution for legacy callers (returns row dicts)."""
        from sqlalchemy import text

        async with engine.connect() as conn:
            result = await conn.execute(text(query), params)
            rows = result.fetchall()
            columns = list(result.keys())
            return [dict(zip(columns, row)) for row in rows]
