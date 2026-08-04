from datetime import datetime

from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    title: str
    url: str
    source: str
    published_at: datetime
    summary: str = ""
    category: str = "general"
    sentiment_score: float | None = None
    entities: list[str] = Field(default_factory=list)


class SentimentResult(BaseModel):
    asset: str
    score: float  # -1..1
    magnitude: float  # 0..1
    label: str  # bullish | bearish | neutral
    article_count: int
    sources: list[str] = Field(default_factory=list)
    window_start: datetime | None = None
    window_end: datetime | None = None
