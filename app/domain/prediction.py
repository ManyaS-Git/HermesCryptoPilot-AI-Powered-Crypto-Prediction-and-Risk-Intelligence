from datetime import datetime

from pydantic import BaseModel, Field


class ModelPrediction(BaseModel):
    """Output of a single prediction model in the ensemble."""
    model_name: str
    direction: str  # UP | DOWN
    probability: float  # 0..1 probability of `direction`
    expected_return: float  # expected return over horizon
    prediction: float | None = None  # absolute price forecast
    confidence_lower: float | None = None
    confidence_upper: float | None = None
    sample_count: int = 0
    details: dict = Field(default_factory=dict)


class EnsemblePrediction(BaseModel):
    asset: str
    interval: str
    horizon_bars: int
    direction: str  # UP | DOWN
    probability: float  # 0..1 calibrated probability of direction
    expected_return: float
    expected_price: float | None = None
    confidence_lower: float | None = None
    confidence_upper: float | None = None
    model_weights: dict = Field(default_factory=dict)
    model_predictions: list[ModelPrediction] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    feature_count: int = 0


class CalibratedPrediction(BaseModel):
    asset: str
    interval: str
    raw_probability: float
    calibrated_probability: float
    direction: str
    expected_return: float
    calibration_method: str = "platt_scaling"
    calibration_bins: int = 0
    sample_count: int = 0


class PredictionRequest(BaseModel):
    asset: str = Field(min_length=1, max_length=16)
    interval: str = "15m"
    horizon_bars: int = Field(default=1, ge=1, le=24)
