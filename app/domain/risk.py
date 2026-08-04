from pydantic import BaseModel, Field


class RiskParameters(BaseModel):
    capital: float = Field(default=10_000.0, gt=0)
    kelly_fraction: float = Field(default=0.25, ge=0, le=1)
    max_position_size: float = Field(default=0.20, ge=0, le=1)
    risk_free_rate: float = Field(default=0.02, ge=0, le=1)
    var_confidence: float = Field(default=0.95, ge=0.5, lt=1)
    monte_carlo_sims: int = Field(default=10_000, ge=100, le=200_000)
    monte_carlo_horizon: int = Field(default=24, ge=1, le=1000)


class RiskMetrics(BaseModel):
    var_95: float
    cvar_95: float
    volatility_annualized: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    monte_carlo_var_95: float | None = None
    monte_carlo_mean_return: float | None = None
    monte_carlo_win_probability: float | None = None
    kelly_fraction: float
    expected_value: float
    beta: float | None = None


class PositionRecommendation(BaseModel):
    asset: str
    interval: str = ""
    direction: str  # UP | DOWN
    expected_value: float
    kelly_size: float
    suggested_position: float  # dollar amount
    stop_loss: float | None = None
    take_profit: float | None = None
    risk_score: float = 0.0  # 0..1
    risk_level: str = "low"  # low | medium | high
    rationale: str = ""


class PortfolioRiskMetrics(BaseModel):
    total_value: float = 0.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    risk_score: float = 0.0
    diversification_score: float = 0.0
    correlation_matrix: dict[str, dict[str, float]] = Field(default_factory=dict)
    allocation: dict[str, float] = Field(default_factory=dict)
    var_95: float = 0.0
    sharpe_ratio: float = 0.0
