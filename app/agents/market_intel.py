"""Market Intelligence Agent: gathers live market microstructure consensus
(order book imbalance, funding, trade flow) for an asset."""
from __future__ import annotations

from app.domain.intel import MarketIntelResult
from app.services.market.intel import MarketIntelService


class MarketIntelAgent:
    def __init__(self, intel: MarketIntelService | None = None) -> None:
        self.intel = intel or MarketIntelService()

    async def get_market_consensus(self, asset: str) -> MarketIntelResult:
        return await self.intel.get_consensus(asset)
