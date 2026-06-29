from app.domain.prediction import SignalFusionResult
from app.domain.risk import PositionRecommendation, RiskParameters
from app.telemetry.logger import setup_telemetry

logger = setup_telemetry(__name__)

class RiskAgent:
    def __init__(self, params: RiskParameters = RiskParameters()):
        self.params = params
        
    async def calculate_kelly_size(self, fusion_result: SignalFusionResult, odds: float = 2.0) -> PositionRecommendation:
        """
        Calculates position size using the Kelly Criterion.
        f* = (p * (b + 1) - 1) / b
        where p is probability of winning, b is the net decimal odds.
        For crypto binary prediction (e.g., polymarket paying 1 to 1), b is typically 1 (net odds).
        """
        logger.info(f"Calculating Kelly size for {fusion_result.asset}")
        
        p = fusion_result.fused_probability
        signal_direction = "UP" if p > 0.5 else "DOWN"
        
        # If signal is down, we are betting on DOWN, so win prob is 1-p
        win_prob = p if signal_direction == "UP" else (1.0 - p)
        
        # Net odds b. If payout is 2.0 decimal, net odds b is 1.0.
        b = odds - 1.0
        
        if b <= 0:
            kelly_f = 0.0
            expected_value = 0.0
            rationale = f"Invalid odds ({odds}). Cannot calculate Kelly."
        else:
            # Expected value
            expected_value = (win_prob * b) - (1.0 - win_prob)
            
            if expected_value > 0:
                # Kelly formula
                kelly_f = ((win_prob * (b + 1.0)) - 1.0) / b
                # Apply risk parameters
                kelly_f = kelly_f * self.params.kelly_fraction
                kelly_f = min(kelly_f, self.params.max_position_size)
                rationale = f"Positive EV ({expected_value:.4f}). Kelly calculated: {kelly_f:.4f} (Max: {self.params.max_position_size})"
            else:
                kelly_f = 0.0
                rationale = f"Negative EV ({expected_value:.4f}). No trade recommended."
                
        logger.info(rationale)
        
        return PositionRecommendation(
            asset=fusion_result.asset,
            signal_direction=signal_direction,
            expected_value=expected_value,
            kelly_size=round(kelly_f, 4),
            rationale=rationale
        )
