from typing import List
from app.domain.market import OHLCV
from app.services.market_data import MarketDataService
from app.telemetry.logger import setup_telemetry

logger = setup_telemetry(__name__)

class MarketDataAgent:
    def __init__(self):
        self.service = MarketDataService()
        
    async def fetch_historical_data(self, asset: str, timeframes: List[str] = ["1m", "5m"], limit: int = 1000) -> dict[str, List[OHLCV]]:
        """
        Fetches multi-timeframe OHLCV data.
        """
        logger.info(f"Fetching historical data for {asset} on timeframes {timeframes}")
        data_dict = {}
        
        # Sequentially or concurrently fetch data for different timeframes
        for tf in timeframes:
            try:
                # Convert common crypto names to Binance pairs
                pair = f"{asset}USDT" if "USDT" not in asset else asset
                data = await self.service.fetch_ohlcv(pair, tf, limit)
                data_dict[tf] = data
            except Exception as e:
                logger.error(f"Failed to fetch {tf} data for {asset}: {e}")
                
        return data_dict
