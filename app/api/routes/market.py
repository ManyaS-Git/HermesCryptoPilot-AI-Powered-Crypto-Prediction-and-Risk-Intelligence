"""Market data endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.domain.market import (
    AssetInfo,
    Candle,
    FearGreedValue,
    FundingRate,
    Liquidation,
    OnChainMetrics,
    OpenInterest,
    OrderBook,
    Ticker,
    Trade,
)
from app.services.intelligence.onchain import OnChainService
from app.services.market.base import ProviderError
from app.services.market.manager import MarketDataManager
from app.services.market.symbols import normalize_asset

router = APIRouter(prefix="/market", tags=["market"])

market = MarketDataManager()
onchain = OnChainService()

VALID_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"}


def _validate_asset(asset: str) -> str:
    normalized = normalize_asset(asset)
    if not normalized or len(normalized) > 16:
        raise HTTPException(400, "Invalid asset symbol")
    return normalized


@router.get("/ticker/{asset}", response_model=Ticker)
async def get_ticker(asset: str) -> Ticker:
    asset = _validate_asset(asset)
    try:
        return await market.get_ticker(asset)
    except ProviderError as exc:
        raise HTTPException(502, str(exc)) from exc


@router.get("/klines/{asset}", response_model=list[Candle])
async def get_klines(
    asset: str, interval: str = "15m", limit: int = 500
) -> list[Candle]:
    asset = _validate_asset(asset)
    if interval not in VALID_INTERVALS:
        raise HTTPException(400, f"Invalid interval. Use one of {sorted(VALID_INTERVALS)}")
    limit = max(10, min(limit, 1000))
    try:
        return await market.get_klines(asset, interval, limit)
    except ProviderError as exc:
        raise HTTPException(502, str(exc)) from exc


@router.get("/assets", response_model=list[AssetInfo])
async def get_assets(top: int = 50) -> list[AssetInfo]:
    try:
        return await market.get_assets(top=min(top, 250))
    except ProviderError as exc:
        raise HTTPException(502, str(exc)) from exc


@router.get("/overview")
async def market_overview():
    try:
        assets, fear_greed, top_gainers, top_losers = await _overview(market)
        return {
            "assets": [a.model_dump() for a in assets[:50]],
            "fear_greed": fear_greed.model_dump() if fear_greed else None,
            "top_gainers": [a.model_dump() for a in top_gainers[:10]],
            "top_losers": [a.model_dump() for a in top_losers[:10]],
        }
    except ProviderError as exc:
        raise HTTPException(502, str(exc)) from exc


@router.get("/fear-greed", response_model=FearGreedValue | None)
async def get_fear_greed() -> FearGreedValue | None:
    return await market.get_fear_greed()


@router.get("/funding/{asset}", response_model=FundingRate | None)
async def get_funding(asset: str) -> FundingRate | None:
    return await market.get_funding_rate(_validate_asset(asset))


@router.get("/open-interest/{asset}", response_model=OpenInterest | None)
async def get_open_interest(asset: str) -> OpenInterest | None:
    return await market.get_open_interest(_validate_asset(asset))


@router.get("/orderbook/{asset}", response_model=OrderBook)
async def get_orderbook(asset: str, limit: int = 20) -> OrderBook:
    asset = _validate_asset(asset)
    try:
        return await market.get_order_book(asset, min(limit, 100))
    except ProviderError as exc:
        raise HTTPException(502, str(exc)) from exc


@router.get("/trades/{asset}", response_model=list[Trade])
async def get_trades(asset: str, limit: int = 100) -> list[Trade]:
    try:
        return await market.get_recent_trades(_validate_asset(asset), min(limit, 500))
    except ProviderError as exc:
        raise HTTPException(502, str(exc)) from exc


@router.get("/liquidations/{asset}", response_model=list[Liquidation])
async def get_liquidations(asset: str) -> list[Liquidation]:
    return await market.get_liquidations(_validate_asset(asset))


@router.get("/onchain/{asset}", response_model=OnChainMetrics)
async def get_onchain(asset: str) -> OnChainMetrics:
    return await onchain.get_metrics(_validate_asset(asset))


async def _overview(market: MarketDataManager):
    assets = await market.get_assets(top=50)
    fear_greed = await market.get_fear_greed()
    gainers = sorted(assets, key=lambda a: a.change_pct_24h, reverse=True)
    losers = sorted(assets, key=lambda a: a.change_pct_24h)
    return assets, fear_greed, gainers, losers
