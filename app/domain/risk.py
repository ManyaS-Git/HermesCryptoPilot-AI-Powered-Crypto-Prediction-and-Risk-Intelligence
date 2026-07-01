from pydantic import BaseModel, Field
from datetime import datetime


class RiskParameters(BaseModel):
    kelly_fraction: float = 1.0  # Full Kelly, Half Kelly, etc.
    max_position_size: float = 0.2  # Max 20% of bankroll per trade


class PositionRecommendation(BaseModel):
    asset: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    signal_direction: str  # "UP" or "DOWN"
    expected_value: float
    kelly_size: float
    rationale: str
