from datetime import datetime

from sqlalchemy import DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utcnow


class PredictionRecord(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "predictions"

    asset: Mapped[str] = mapped_column(String(16), index=True)
    interval: Mapped[str] = mapped_column(String(8), default="15m")
    horizon_bars: Mapped[int] = mapped_column(default=1)
    direction: Mapped[str] = mapped_column(String(8))  # UP | DOWN
    probability: Mapped[float] = mapped_column(Float, default=0.5)
    expected_return: Mapped[float] = mapped_column(Float, default=0.0)
    expected_price: Mapped[float] = mapped_column(Float, nullable=True)
    target_price: Mapped[float] = mapped_column(Float, nullable=True)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=True)
    confidence_lower: Mapped[float] = mapped_column(Float, nullable=True)
    confidence_upper: Mapped[float] = mapped_column(Float, nullable=True)
    model_ensemble: Mapped[str] = mapped_column(String(255), default="")
    signal_direction: Mapped[str] = mapped_column(String(8), nullable=True)
    kelly_size: Mapped[float] = mapped_column(Float, default=0.0)
    expected_value: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    var_95: Mapped[float] = mapped_column(Float, nullable=True)
    sharpe_ratio: Mapped[float] = mapped_column(Float, nullable=True)
    sortino_ratio: Mapped[float] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[float] = mapped_column(Float, nullable=True)
    fused_probability: Mapped[float] = mapped_column(Float, nullable=True)
    fusion_weights: Mapped[dict] = mapped_column(JSON, default=dict)
    technical_probability: Mapped[float] = mapped_column(Float, nullable=True)
    consensus_probability: Mapped[float] = mapped_column(Float, nullable=True)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=True)
    market_regime: Mapped[str] = mapped_column(String(32), default="unknown")
    model_predictions: Mapped[dict] = mapped_column(JSON, default=dict)
    indicators: Mapped[dict] = mapped_column(JSON, default=dict)
    rationale: Mapped[str] = mapped_column(String(4096), default="")
    llm_summary: Mapped[str] = mapped_column(String(4096), default="")
    status: Mapped[str] = mapped_column(String(16), default="completed")
    evaluated: Mapped[bool] = mapped_column(default=False)


class AgentRun(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "agent_runs"

    agent_name: Mapped[str] = mapped_column(String(64), index=True)
    asset: Mapped[str] = mapped_column(String(16), default="")
    status: Mapped[str] = mapped_column(String(16), default="running")
    execution_time_ms: Mapped[float] = mapped_column(Float, nullable=True)
    error_message: Mapped[str] = mapped_column(String(1024), default="")
    output_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Backtest(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "backtests"

    asset: Mapped[str] = mapped_column(String(16), index=True)
    interval: Mapped[str] = mapped_column(String(8), default="15m")
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    initial_capital: Mapped[float] = mapped_column(Float, default=10000.0)
    final_capital: Mapped[float] = mapped_column(Float, nullable=True)
    total_return: Mapped[float] = mapped_column(Float, nullable=True)
    sharpe_ratio: Mapped[float] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[float] = mapped_column(Float, nullable=True)
    metrics_json: Mapped[dict] = mapped_column(JSON, default=dict)
    trades_json: Mapped[list] = mapped_column(JSON, default=list)


class SignalFusionRecord(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "signal_fusion_records"

    asset: Mapped[str] = mapped_column(String(16), index=True)
    calibrated_probability: Mapped[float] = mapped_column(Float, nullable=True)
    consensus_probability: Mapped[float] = mapped_column(Float, nullable=True)
    fused_probability: Mapped[float] = mapped_column(Float, nullable=True)
    weights_json: Mapped[dict] = mapped_column(JSON, default=dict)
    market_regime: Mapped[str] = mapped_column(String(32), default="unknown")
    rationale: Mapped[str] = mapped_column(String(2048), default="")
