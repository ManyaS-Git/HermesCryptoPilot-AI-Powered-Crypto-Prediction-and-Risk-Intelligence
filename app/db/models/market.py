from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IntPrimaryKeyMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WatchlistItem(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "watchlist_items"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    asset: Mapped[str] = mapped_column(String(16), index=True)
    quote: Mapped[str] = mapped_column(String(8), default="USDT")

    user = relationship("User", back_populates="watchlist")


class Alert(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "alerts"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    asset: Mapped[str] = mapped_column(String(16), index=True)
    alert_type: Mapped[str] = mapped_column(String(32))  # price | prediction | risk
    condition: Mapped[str] = mapped_column(String(8), default=">")  # > < >= <=
    threshold: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_checked_price: Mapped[float] = mapped_column(Float, default=0.0)

    user = relationship("User", back_populates="alerts")


class MarketSnapshot(Base, IntPrimaryKeyMixin):
    __tablename__ = "market_snapshots"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True
    )
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    asset: Mapped[str] = mapped_column(String(16), index=True)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    change_24h: Mapped[float] = mapped_column(Float, default=0.0)
    volume_24h: Mapped[float] = mapped_column(Float, default=0.0)
    high_24h: Mapped[float] = mapped_column(Float, default=0.0)
    low_24h: Mapped[float] = mapped_column(Float, default=0.0)
    funding_rate: Mapped[float] = mapped_column(Float, nullable=True)
    open_interest: Mapped[float] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="")


class NewsArticle(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "news_articles"

    title: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(String(1024), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(64))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    summary: Mapped[str] = mapped_column(String(2048), default="")
    category: Mapped[str] = mapped_column(String(64), default="general")
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=True)
    entities: Mapped[list] = mapped_column(JSON, default=list)


class SentimentRecord(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "sentiment_records"

    asset: Mapped[str] = mapped_column(String(16), index=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)  # -1..1
    magnitude: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(64), default="news")
    article_count: Mapped[int] = mapped_column(default=0)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
