"""On-chain intelligence.

Real data sources:
- mempool.space (public, keyless) for Bitcoin mempool & fee estimates.
- Whale Alert API when WHALE_ALERT_KEY is configured.
- Etherscan when ETHERSCAN_API_KEY is configured (large transactions).

Unavailable providers degrade gracefully (empty / partial results, never
fabricated values).
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.core.cache import get_cache
from app.core.config import get_settings
from app.domain.market import OnChainMetrics, WhaleTransaction
from app.services.market.clients import provider_get


class OnChainService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = get_cache()

    async def get_metrics(self, asset: str) -> OnChainMetrics:
        cache_key = f"onchain:{asset.upper()}"
        cached = await self.cache.get(cache_key)
        if cached:
            return OnChainMetrics.model_validate(cached)

        metrics = OnChainMetrics(asset=asset.upper(), source="")

        if asset.upper() == "BTC":
            try:
                resp = await provider_get(
                    "https://mempool.space/api/v1/fees/recommended",
                    provider="mempool", rps=5,
                )
                fees = resp.json()
                metrics.btc_fee_estimate = {
                    "fastest": fees.get("fastestFee"),
                    "half_hour": fees.get("halfHourFee"),
                    "hour": fees.get("hourFee"),
                    "economy": fees.get("economyFee"),
                }
                metrics.source = "mempool.space"
            except Exception:
                pass
            try:
                resp = await provider_get(
                    "https://mempool.space/api/mempool", provider="mempool", rps=5
                )
                mempool = resp.json()
                metrics.mempool_size = int(mempool.get("count", 0))
            except Exception:
                pass

        if asset.upper() in ("BTC", "ETH") and self.settings.WHALE_ALERT_KEY:
            try:
                resp = await provider_get(
                    "https://api.whale-alert.io/v1/transactions",
                    params={"api_key": self.settings.WHALE_ALERT_KEY, "min_value": 1000000},
                    provider="whalealert", rps=5,
                )
                for tx in resp.json().get("transactions", [])[:10]:
                    symbol = (tx.get("symbol") or asset.upper()).upper()
                    if symbol != asset.upper():
                        continue
                    metrics.whale_transactions.append(
                        WhaleTransaction(
                            asset=symbol,
                            symbol=symbol,
                            amount=float(tx.get("amount", 0)),
                            usd_value=float(tx.get("amount_usd", 0)),
                            from_address=tx.get("from", {}).get("address", ""),
                            to_address=tx.get("to", {}).get("address", ""),
                            timestamp=datetime.fromtimestamp(tx.get("timestamp", 0), tz=timezone.utc),
                            kind=tx.get("transaction_type", "whale_movement"),
                            source="whale_alert",
                        )
                    )
                if metrics.whale_transactions:
                    metrics.source = metrics.source or "whale_alert"
            except Exception:
                pass

        if asset.upper() == "ETH" and self.settings.ETHERSCAN_API_KEY:
            try:
                resp = await provider_get(
                    "https://api.etherscan.io/api",
                    params={
                        "module": "account",
                        "action": "txlist",
                        "address": "0x28c6c06298d514db089934071355e5743bf21d60",  # Binance hot wallet
                        "startblock": 0,
                        "endblock": 99999999,
                        "page": 1,
                        "offset": 10,
                        "sort": "desc",
                        "apikey": self.settings.ETHERSCAN_API_KEY,
                    },
                    provider="etherscan", rps=5,
                )
                for tx in resp.json().get("result", [])[:10]:
                    value = float(tx.get("value", 0)) / 1e18
                    if value >= 500:
                        metrics.whale_transactions.append(
                            WhaleTransaction(
                                asset="ETH", symbol="ETH", amount=value,
                                usd_value=0.0,
                                from_address=tx.get("from", ""),
                                to_address=tx.get("to", ""),
                                timestamp=datetime.fromtimestamp(int(tx.get("timeStamp", 0)), tz=timezone.utc),
                                kind="large_transaction", source="etherscan",
                            )
                        )
            except Exception:
                pass

        await self.cache.set(cache_key, metrics.model_dump(), ttl=300)
        return metrics
