"""Async database engine and session management."""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.db.base import Base


def build_engine() -> AsyncEngine:
    settings = get_settings()
    connect_args = {}
    pool_kwargs: dict = {}
    if settings.is_sqlite:
        connect_args = {"check_same_thread": False}
        # aiosqlite doesn't support connection pooling; NullPool matches the
        # previous sync sqlite3 session-per-request behaviour.
        pool_kwargs = {"poolclass": NullPool}
    else:
        pool_kwargs = {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
        }
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        connect_args=connect_args,
        **pool_kwargs,
    )


engine = build_engine()
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create tables if they don't exist (dev convenience).

    In production, use Alembic migrations. This mirrors the previous
    DatabaseManager.init_db contract but through SQLAlchemy metadata.
    """
    settings = get_settings()
    if settings.is_sqlite:
        # ensure the data directory exists for file-based SQLite
        import re

        match = re.match(r"sqlite\+aiosqlite:///(.+)", settings.DATABASE_URL)
        if match:
            import pathlib

            path = pathlib.Path(match.group(1))
            path.parent.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def check_database_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def dispose_engine() -> None:
    await engine.dispose()
