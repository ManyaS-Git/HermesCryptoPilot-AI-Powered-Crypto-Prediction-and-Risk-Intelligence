from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Portfolio(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "portfolios"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(128), default="Main Portfolio")
    cash_balance: Mapped[float] = mapped_column(Float, default=0.0)
    base_currency: Mapped[str] = mapped_column(String(8), default="USDT")

    user = relationship("User", back_populates="portfolios")
    positions = relationship(
        "Position", back_populates="portfolio", cascade="all, delete-orphan"
    )


class Position(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "positions"

    portfolio_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), index=True
    )
    asset: Mapped[str] = mapped_column(String(16), index=True)
    symbol: Mapped[str] = mapped_column(String(32))
    side: Mapped[str] = mapped_column(String(8), default="long")  # long | short
    quantity: Mapped[float] = mapped_column(Float, default=0.0)
    entry_price: Mapped[float] = mapped_column(Float, default=0.0)
    current_price: Mapped[float] = mapped_column(Float, default=0.0)
    leverage: Mapped[float] = mapped_column(Float, default=1.0)
    unrealized_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    realized_pnl: Mapped[float] = mapped_column(Float, default=0.0)

    portfolio = relationship("Portfolio", back_populates="positions")
