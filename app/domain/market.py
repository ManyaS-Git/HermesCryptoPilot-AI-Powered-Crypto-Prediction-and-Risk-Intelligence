from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class OHLCV(BaseModel):
    asset: str
    timestamp: datetime
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class MarketOdds(BaseModel):
    asset: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str  # Polymarket, Kalshi
    implied_probability: float
    odds: float
    
class UnifiedMarketConsensus(BaseModel):
    asset: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    unified_probability: float
    sources_used: List[str]
