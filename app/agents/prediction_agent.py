from typing import List
from app.domain.market import OHLCV
from app.domain.prediction import KronosPrediction
from app.services.kronos import KronosService
from app.telemetry.logger import setup_telemetry

logger = setup_telemetry(__name__)

class PredictionAgent:
    def __init__(self):
        self.kronos = KronosService()
        
    async def run_prediction(self, data_dict: dict[str, List[OHLCV]]) -> dict[str, KronosPrediction]:
        """
        Runs predictions for multiple timeframes.
        """
        predictions = {}
        for timeframe, ohlcv_list in data_dict.items():
            if not ohlcv_list:
                logger.warning(f"Skipping prediction for {timeframe} due to lack of data.")
                continue
                
            try:
                prediction = await self.kronos.predict(ohlcv_list)
                predictions[timeframe] = prediction
            except Exception as e:
                logger.error(f"Prediction failed for {timeframe}: {e}")
                
        return predictions
