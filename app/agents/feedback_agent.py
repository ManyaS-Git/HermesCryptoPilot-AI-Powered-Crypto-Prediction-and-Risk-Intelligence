from typing import Any
from app.telemetry.logger import setup_telemetry
from app.services.storage import DatabaseManager

logger = setup_telemetry(__name__)

class FeedbackAgent:
    def __init__(self):
        self.db = DatabaseManager()
        
    async def update_memory(self, prediction_result: dict, market_result: dict, final_decision: dict):
        """
        Updates the agent's short-term memory (Hermes) and long-term DB metrics.
        """
        logger.info(f"Feedback Agent: Updating memory with final decision for {final_decision.get('asset')}")
        
        # In a real Hermes framework, we would use the memory API to inject context:
        # hermes.memory.add_context(f"Recent trade decision on {asset}: {final_decision['rationale']}")
        
        # We simulate writing the outcomes to the DB for the EvaluationAgent to use later
        query = '''
            INSERT INTO position_recommendations (asset, signal_direction, kelly_size, fused_probability, expected_value, rationale)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (
            final_decision.get('asset'),
            final_decision.get('signal_direction'),
            final_decision.get('kelly_size'),
            final_decision.get('fused_probability'),
            final_decision.get('expected_value'),
            final_decision.get('rationale')
        )
        await self.db.execute_query(query, params)
        
        logger.info("Feedback loop complete. Memory and DB updated.")
