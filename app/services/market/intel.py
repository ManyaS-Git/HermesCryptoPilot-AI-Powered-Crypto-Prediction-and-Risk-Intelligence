"""Market intelligence: derive a consensus probability from real market
microstructure — order book imbalance, funding rate, and trade aggressor
balance. All inputs come from live exchange data.
"""
from __future__ import annotations

import numpy as np

from app.domain.intel import MarketIntelResult, UnifiedMarketConsensus
from app.services.market.base import ProviderError
from app.services.market.manager import MarketDataManager
from app.services.market.symbols import normalize_asset


class MarketIntelService:
    def __init__(self, market: MarketDataManager | None = None) -> None:
        self.market = market or MarketDataManager()

    async def get_consensus(self, asset: str) -> MarketIntelResult:
        asset = normalize_asset(asset)
        sources: list[str] = []
        components: dict[str, float] = {}

        # 1. Order book imbalance (-1..1)
        try:
            book = await self.market.get_order_book(asset, limit=20)
            bid_vol = sum(l.quantity for l in book.bids)
            ask_vol = sum(l.quantity for l in book.asks)
            total = bid_vol + ask_vol
            imbalance = (bid_vol - ask_vol) / total if total > 0 else 0.0
            components["orderbook"] = float(np.clip(imbalance, -1, 1))
            sources.append("orderbook")
            top_bid = book.bids[0].price if book.bids else None
            top_ask = book.asks[0].price if book.asks else None
        except (ProviderError, Exception):  # noqa: BLE001
            imbalance = 0.0
            top_bid = top_ask = None

        # 2. Funding rate signal (-1..1)
        try:
            funding = await self.market.get_funding_rate(asset)
            if funding is not None and funding.funding_rate != 0:
                # Positive funding = longs pay shorts -> crowded long, contrarian-ish
                components["funding"] = float(np.clip(-funding.funding_rate * 5000, -1, 1))
                sources.append("funding")
        except (ProviderError, Exception):  # noqa: BLE001
            pass

        # 3. Trade aggressor balance (-1..1)
        try:
            trades = await self.market.get_recent_trades(asset, limit=200)
            if trades:
                buy_vol = sum(t.quantity for t in trades if t.side == "buy")
                sell_vol = sum(t.quantity for t in trades if t.side == "sell")
                total = buy_vol + sell_vol
                trade_imb = (buy_vol - sell_vol) / total if total > 0 else 0.0
                components["trades"] = float(np.clip(trade_imb, -1, 1))
                sources.append("trades")
        except (ProviderError, Exception):  # noqa: BLE001
            pass

        # 4. Combine into an UP probability
        if not sources:
            consensus_probability = 0.5
            rationale = "No live microstructure data available."
        else:
            mean_signal = float(np.mean(list(components.values())))
            # Map the microstructure signal into probability space
            consensus_probability = float(1 / (1 + np.exp(-2.0 * mean_signal)))
            consensus_probability = float(np.clip(consensus_probability, 0.05, 0.95))
            rationale = (
                f"Consensus from {', '.join(sources)}: signal {mean_signal:+.3f} -> "
                f"UP probability {consensus_probability:.2f}."
            )

        spread_pct = None
        if top_bid and top_ask and top_bid > 0:
            spread_pct = round((top_ask - top_bid) / top_bid * 100, 4)

        consensus = UnifiedMarketConsensus(
            asset=asset,
            consensus_probability=round(consensus_probability, 4),
            orderbook_imbalance=round(components.get("orderbook", 0.0), 4),
            funding_signal=round(components.get("funding", 0.0), 4),
            trade_imbalance=round(components.get("trades", 0.0), 4),
            sources_used=sources,
            rationale=rationale,
        )
        return MarketIntelResult(
            asset=asset,
            consensus=consensus,
            top_ask_price=top_ask,
            top_bid_price=top_bid,
            spread_pct=spread_pct,
        )
