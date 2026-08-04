"""CoinGecko market data provider (assets, prices, fear & greed index).

Uses the public API; supports an optional API key for higher rate limits.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import get_settings
from app.domain.market import AssetInfo, Candle, FearGreedValue, Ticker
from app.services.market.base import MarketDataProvider, ProviderError
from app.services.market.clients import provider_get
from app.services.market.symbols import coingecko_id


class CoinGeckoProvider(MarketDataProvider):
    name = "coingecko"

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.COINGECKO_BASE_URL
        self.api_key = settings.COINGECKO_API_KEY

    def _headers(self) -> dict | None:
        if self.api_key:
            return {"x-cg-demo-api-key": self.api_key}
        return None

    async def get_ticker(self, asset: str) -> Ticker:
        cg_id = coingecko_id(asset)
        try:
            resp = await provider_get(
                f"{self.base_url}/coins/{cg_id}",
                params={
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "true",
                },
                headers=self._headers(),
                provider="coingecko",
                rps=5,
            )
            data = resp.json()
            md = data.get("market_data", {})
            return Ticker(
                symbol=asset.upper(),
                asset=asset.upper(),
                price=float(md["current_price"].get("usd", 0) or 0),
                change_24h=float(md["price_change_24h"] or 0),
                change_pct_24h=float(md["price_change_percentage_24h"] or 0),
                volume_24h=float(md["total_volume"].get("usd", 0) or 0),
                high_24h=float(md.get("high_24h", {}).get("usd", 0) or 0),
                low_24h=float(md.get("low_24h", {}).get("usd", 0) or 0),
                market_cap=float(md.get("market_cap", {}).get("usd", 0) or 0),
                source=self.name,
            )
        except Exception as exc:
            raise ProviderError(f"CoinGecko ticker failed: {exc}") from exc

    async def get_klines(self, asset: str, interval: str, limit: int = 500) -> list[Candle]:
        # CoinGecko's public chart endpoint is rate limited; delegates to spot
        # providers. Implemented to satisfy the interface contract.
        raise ProviderError("CoinGecko does not provide klines via public API")

    async def get_assets(self, vs_currency: str = "usd", top: int = 50) -> list[AssetInfo]:
        try:
            resp = await provider_get(
                f"{self.base_url}/coins/markets",
                params={"vs_currency": vs_currency, "order": "market_cap_desc",
                        "per_page": min(top, 250), "page": 1, "sparkline": "false"},
                headers=self._headers(),
                provider="coingecko",
                rps=5,
            )
            return [
                AssetInfo(
                    asset=d["symbol"].upper(),
                    name=d["name"],
                    symbol=d["symbol"].upper(),
                    price=float(d["current_price"] or 0),
                    change_pct_24h=float(d["price_change_percentage_24h"] or 0),
                    volume_24h=float(d["total_volume"] or 0),
                    market_cap=float(d["market_cap"] or 0),
                    image=d.get("image"),
                    source=self.name,
                )
                for d in resp.json()
            ]
        except Exception as exc:
            raise ProviderError(f"CoinGecko assets failed: {exc}") from exc

    async def get_fear_greed(self) -> FearGreedValue | None:
        try:
            resp = await provider_get(
                "https://api.alternative.me/fng/", params={"limit": 1}, provider="fng", rps=5
            )
            data = resp.json()["data"][0]
            return FearGreedValue(
                value=int(data["value"]),
                value_classification=data["value_classification"],
                timestamp=datetime.fromtimestamp(int(data["timestamp"]), tz=timezone.utc),
                source="alternative.me",
            )
        except Exception:
            return None
