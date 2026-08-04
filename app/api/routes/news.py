"""News, sentiment, and analysis endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.domain.news import NewsArticle, SentimentResult
from app.services.intelligence.news import NewsService
from app.services.intelligence.sentiment import SentimentService
from app.services.market.symbols import normalize_asset
from app.agents.data_agent import MarketDataAgent

router = APIRouter(tags=["intelligence"])

news_service = NewsService()
sentiment_service = SentimentService()
data_agent = MarketDataAgent()


@router.get("/news", response_model=list[NewsArticle])
async def get_news(limit: int = 30) -> list[NewsArticle]:
    return await news_service.fetch_news(limit=min(limit, 100))


@router.get("/news/sentiment/{asset}", response_model=SentimentResult)
async def get_sentiment(asset: str, hours: int = 24) -> SentimentResult:
    return await sentiment_service.analyze(normalize_asset(asset), hours=hours)


@router.get("/analysis/{asset}")
async def get_analysis(asset: str, interval: str = "15m"):
    asset = normalize_asset(asset)
    try:
        return await data_agent.get_indicators(asset, interval=interval)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"Analysis failed: {exc}") from exc
