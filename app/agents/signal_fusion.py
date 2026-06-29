from typing import List, Protocol
from app.domain.prediction import CalibratedPrediction, SignalFusionResult
from app.domain.market import UnifiedMarketConsensus
from app.telemetry.logger import setup_telemetry

logger = setup_telemetry(__name__)

class FusionStrategy(Protocol):
    def fuse(self, technicals: CalibratedPrediction, consensus: UnifiedMarketConsensus) -> SignalFusionResult:
        ...

class ConfidenceWeightedAverage(FusionStrategy):
    def __init__(self, tech_weight: float = 0.6, cons_weight: float = 0.4):
        self.tech_weight = tech_weight
        self.cons_weight = cons_weight
        
    def fuse(self, technicals: CalibratedPrediction, consensus: UnifiedMarketConsensus) -> SignalFusionResult:
        tech_prob = technicals.calibrated_probability
        if technicals.prediction.predicted_move == "DOWN":
            tech_prob = 1.0 - tech_prob # Normalize to UP probability
            
        cons_prob = consensus.unified_probability
        
        # Weighted average
        fused_prob = (tech_prob * self.tech_weight) + (cons_prob * self.cons_weight)
        
        rationale = f"Fused using Confidence-Weighted Average (Tech: {self.tech_weight}, Cons: {self.cons_weight}). Tech prob: {tech_prob:.4f}, Cons prob: {cons_prob:.4f}."
        
        return SignalFusionResult(
            asset=technicals.prediction.asset,
            fused_probability=round(fused_prob, 4),
            fusion_strategy="Confidence-Weighted Average",
            rationale=rationale
        )

class SignalFusionAgent:
    def __init__(self, strategy: FusionStrategy = ConfidenceWeightedAverage()):
        self.strategy = strategy
        
    async def fuse_signals(self, technicals: CalibratedPrediction, consensus: UnifiedMarketConsensus) -> SignalFusionResult:
        logger.info(f"Fusing signals for {technicals.prediction.asset}")
        return self.strategy.fuse(technicals, consensus)
