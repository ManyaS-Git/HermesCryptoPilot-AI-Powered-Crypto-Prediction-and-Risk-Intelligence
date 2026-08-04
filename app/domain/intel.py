from datetime import datetime

from pydantic import BaseModel, Field


class UnifiedMarketConsensus(BaseModel):
    """Market-derived consensus probability of an UP move over the horizon.

    Computed from real market microstructure (order book imbalance, funding
    rate, trade aggressor balance) — not from fabricated prediction-market
    odds.
    """
    asset: str
    consensus_probability: float  # 0..1 probability of UP
    orderbook_imbalance: float = 0.0  # -1..1
    funding_signal: float = 0.0  # -1..1
    trade_imbalance: float = 0.0  # -1..1
    sources_used: list[str] = Field(default_factory=list)
    rationale: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MarketIntelResult(BaseModel):
    asset: str
    consensus: UnifiedMarketConsensus
    top_ask_price: float | None = None
    top_bid_price: float | None = None
    spread_pct: float | None = None
