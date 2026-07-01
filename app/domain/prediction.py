from pydantic import BaseModel, Field
from datetime import datetime


class KronosPrediction(BaseModel):
    asset: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    timeframe: str
    predicted_move: str  # "UP" or "DOWN"
    raw_probability: float
    model_version: str


class CalibratedPrediction(BaseModel):
    prediction: KronosPrediction
    calibrated_probability: float
    calibration_method: str  # e.g., "platt_scaling", "isotonic"


class SignalFusionResult(BaseModel):
    asset: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    fused_probability: float
    fusion_strategy: str
    rationale: str
