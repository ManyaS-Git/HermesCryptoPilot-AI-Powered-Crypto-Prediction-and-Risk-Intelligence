import asyncio
from app.domain.market import UnifiedMarketConsensus
from app.services.polymarket import PolymarketService
from app.services.kalshi import KalshiService
from app.services.apify import ApifyService
from app.telemetry.logger import setup_telemetry

logger = setup_telemetry(__name__)


class MarketIntelAgent:
    def __init__(self):
        self.polymarket = PolymarketService()
        self.kalshi = KalshiService()
        self.apify = ApifyService()

    async def get_market_consensus(self, asset: str) -> UnifiedMarketConsensus:
        """
        Gathers odds from multiple prediction markets and unifies them.
        """
        logger.info(f"Gathering market intelligence for {asset}")

        # Concurrent fetching
        results = await asyncio.gather(
            self.polymarket.fetch_odds(asset),
            self.kalshi.fetch_odds(asset),
            return_exceptions=True,
        )

        valid_probs = []
        sources = []

        for result in results:
            if not isinstance(result, Exception) and result is not None:
                valid_probs.append(result.implied_probability)
                sources.append(result.source)

        if not valid_probs:
            logger.warning(
                f"No API odds found for {asset}. Falling back to Apify sentiment scraping."
            )
            sentiment = await self.apify.scrape_sentiment(f"{asset} crypto prediction")
            # Mocking sentiment-based probability calculation
            unified_prob = 0.5 + (0.1 if "Positive" in sentiment else -0.1)
            sources.append("Apify (Sentiment)")
        else:
            # Simple average for now
            unified_prob = sum(valid_probs) / len(valid_probs)

        logger.info(
            f"Market consensus for {asset}: {unified_prob:.4f} (Sources: {sources})"
        )

        return UnifiedMarketConsensus(
            asset=asset, unified_probability=unified_prob, sources_used=sources
        )
