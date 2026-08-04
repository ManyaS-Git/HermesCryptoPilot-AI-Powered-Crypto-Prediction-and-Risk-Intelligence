"""FastAPI application factory.

- Lifespan handles DB initialisation (fixing the previous "never called"
  bug) and starts/stops the real-time price streaming hub.
- All REST routes are under /api/v1.
- Legacy /api/health-check is preserved for backward compatibility.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import agents, auth, market, news, portfolio, predictions, ws
from app.core.config import get_settings
from app.core.logging import init_sentry
from app.db.session import dispose_engine, init_db
from app.services.ws.hub import get_hub

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_sentry()
    await init_db()
    await get_hub().start()
    logger.info("Hermes API ready (env=%s)", settings.ENVIRONMENT)
    try:
        yield
    finally:
        await get_hub().stop()
        await dispose_engine()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "AI-powered cryptocurrency intelligence platform: multi-agent predictions, "
        "real market data, risk analytics, and live streaming."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(news.router, prefix="/api/v1")
app.include_router(portfolio.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")


@app.get("/api/health-check")
async def health_check():
    return {"status": "online", "app": settings.APP_NAME, "version": settings.VERSION}


@app.get("/api/v1/health")
async def health_v1():
    from app.db.session import check_database_connection

    db_ok = await check_database_connection()
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_ok else "unavailable",
        "llm_configured": bool(settings.OPENROUTER_API_KEY),
    }


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
