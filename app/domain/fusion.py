from datetime import datetime

from pydantic import BaseModel, Field


class SignalFusionResult(BaseModel):
    asset: str
    fused_probability: float  # 0..1 probability of UP
    direction: str  # UP | DOWN
    technical_probability: float
    consensus_probability: float
    sentiment_score: float | None = None
    weights: dict[str, float] = Field(default_factory=dict)
    market_regime: str = "unknown"
    rationale: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MarketRegime(BaseModel):
    regime: str  # trending_up | trending_down | ranging | high_volatility
    volatility: float
    trend_strength: float
    adx: float | None = None
    atr_pct: float | None = None
    support: float | None = None
    resistance: float | None = None
