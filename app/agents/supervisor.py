import asyncio
import os
import aiohttp
from app.telemetry.logger import setup_telemetry
from app.agents.market_intel import MarketIntelAgent
from app.agents.data_agent import MarketDataAgent
from app.agents.prediction_agent import PredictionAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.signal_fusion import SignalFusionAgent
from app.agents.risk_agent import RiskAgent
from app.agents.feedback_agent import FeedbackAgent
from app.config.settings import get_settings

logger = setup_telemetry(__name__)
settings = get_settings()

class SupervisorAgent:
    def __init__(self):
        self.market_intel = MarketIntelAgent()
        self.data_agent = MarketDataAgent()
        self.prediction_agent = PredictionAgent()
        self.evaluation_agent = EvaluationAgent()
        self.signal_fusion = SignalFusionAgent()
        self.risk_agent = RiskAgent()
        self.feedback_agent = FeedbackAgent()
        
    async def invoke_llm(self, prompt: str) -> str:
        """
        Calls OpenRouter to perform LLM-based reasoning and summarization.
        """
        if not settings.OPENROUTER_API_KEY:
            logger.warning("OpenRouter API Key not set. Using deterministic fallback reasoning.")
            return "Fallback LLM reasoning: The signals suggest cautious trading based on mixed market and technical indicators."
            
        logger.info(f"Invoking LLM ({settings.LLM_MODEL}) for reasoning.")
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/nousresearch/hermes-agent",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload) as resp:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            return "Fallback LLM reasoning due to API failure."

    async def run_workflow(self, asset: str):
        """
        Main orchestration loop.
        """
        logger.info(f"Supervisor Agent starting workflow for {asset}")
        
        # 1. Fetch Market Intel & Historical Data concurrently
        logger.info("Delegating to Market Intel and Data agents...")
        consensus_task = self.market_intel.get_market_consensus(asset)
        data_task = self.data_agent.fetch_historical_data(asset, timeframes=["5m"], limit=100)
        
        consensus, data_dict = await asyncio.gather(consensus_task, data_task)
        
        if not data_dict or "5m" not in data_dict or not data_dict["5m"]:
            logger.error("Failed to retrieve historical data. Aborting workflow.")
            return
            
        # 2. Run Technical Prediction
        logger.info("Delegating to Prediction Agent...")
        predictions = await self.prediction_agent.run_prediction(data_dict)
        raw_prediction = predictions.get("5m")
        if not raw_prediction:
            logger.error("Failed to generate prediction.")
            return
            
        # 3. Calibrate Prediction
        logger.info("Delegating to Evaluation Agent for calibration...")
        calibrated_prediction = await self.evaluation_agent.calibrate(raw_prediction)
        
        # 4. Signal Fusion
        logger.info("Delegating to Signal Fusion Agent...")
        fused_signal = await self.signal_fusion.fuse_signals(calibrated_prediction, consensus)
        
        # 5. Risk / Kelly Sizing
        logger.info("Delegating to Risk Agent...")
        # Assume decimal odds of 2.0 (1:1 payout) for simple binary option
        position_rec = await self.risk_agent.calculate_kelly_size(fused_signal, odds=2.0)
        
        # 6. LLM Reasoning / Reporting
        prompt = f"""
        Asset: {asset}
        Market Consensus Prob: {consensus.unified_probability}
        Kronos Technical Prob (Calibrated): {calibrated_prediction.calibrated_probability}
        Fused Prob: {fused_signal.fused_probability}
        Risk Recommendation: {position_rec.rationale}
        
        Please provide a short, executive summary explaining this trade rationale, resolving any disagreements between the technicals and the market.
        """
        llm_report = await self.invoke_llm(prompt)
        logger.info(f"LLM Rationale: \n{llm_report}")
        
        # 7. Feedback / Memory Update
        await self.feedback_agent.update_memory(
            prediction_result=calibrated_prediction.model_dump(),
            market_result=consensus.model_dump(),
            final_decision=position_rec.model_dump()
        )
        
        logger.info(f"Supervisor Agent completed workflow for {asset}")
        return position_rec
