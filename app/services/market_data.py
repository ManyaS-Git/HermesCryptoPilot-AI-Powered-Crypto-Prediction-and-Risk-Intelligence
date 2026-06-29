import aiohttp
from datetime import datetime
from typing import List
from app.domain.market import OHLCV
from app.telemetry.logger import setup_telemetry
import logging

logger = setup_telemetry(__name__)

class MarketDataService:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        
    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int = 1000) -> List[OHLCV]:
        """
        Fetches OHLCV data from Binance.
        symbol: e.g. 'BTCUSDT'
        interval: e.g. '1m', '5m'
        """
        from app.config.settings import get_settings
        settings = get_settings()
        
        if settings.MOCK_MODE:
            logger.info(f"MOCK MODE: Returning fake OHLCV data for {symbol}")
            import random
            from datetime import timedelta
            now = datetime.utcnow()
            return [
                OHLCV(
                    asset=symbol,
                    timestamp=now - timedelta(minutes=i*5),
                    timeframe=interval,
                    open=random.uniform(50000, 60000),
                    high=random.uniform(60000, 61000),
                    low=random.uniform(49000, 50000),
                    close=random.uniform(50000, 60000),
                    volume=random.uniform(10, 100)
                ) for i in range(100)
            ]
            
        url = f"{self.base_url}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        logger.info(f"Fetching {limit} bars of {interval} data for {symbol} from Binance.")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch data from Binance: {response.status}")
                    response.raise_for_status()
                    
                data = await response.json()
                
                # Binance kline format:
                # [Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore]
                ohlcv_list = []
                for row in data:
                    ohlcv = OHLCV(
                        asset=symbol,
                        timestamp=datetime.utcfromtimestamp(row[0] / 1000.0),
                        timeframe=interval,
                        open=float(row[1]),
                        high=float(row[2]),
                        low=float(row[3]),
                        close=float(row[4]),
                        volume=float(row[5])
                    )
                    ohlcv_list.append(ohlcv)
                    
                return ohlcv_list
