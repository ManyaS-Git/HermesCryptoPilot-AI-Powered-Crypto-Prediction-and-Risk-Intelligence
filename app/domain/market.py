from datetime import datetime

from pydantic import BaseModel, Field


class Candle(BaseModel):
    """OHLCV bar from a real exchange."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class Ticker(BaseModel):
    symbol: str
    asset: str
    price: float
    change_24h: float
    change_pct_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    market_cap: float | None = None
    source: str = ""


class FundingRate(BaseModel):
    symbol: str
    asset: str
    funding_rate: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = ""


class OpenInterest(BaseModel):
    symbol: str
    asset: str
    open_interest: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = ""


class OrderBookLevel(BaseModel):
    price: float
    quantity: float


class OrderBook(BaseModel):
    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = ""


class Trade(BaseModel):
    symbol: str
    price: float
    quantity: float
    side: str  # buy | sell
    timestamp: datetime
    source: str = ""


class Liquidation(BaseModel):
    symbol: str
    price: float
    quantity: float
    side: str  # long | short
    timestamp: datetime
    source: str = ""


class AssetInfo(BaseModel):
    asset: str
    name: str
    symbol: str
    price: float
    change_pct_24h: float
    volume_24h: float
    market_cap: float | None = None
    image: str | None = None
    source: str = ""


class FearGreedValue(BaseModel):
    value: int
    value_classification: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = ""


class WhaleTransaction(BaseModel):
    asset: str
    symbol: str
    amount: float
    usd_value: float
    from_address: str = ""
    to_address: str = ""
    timestamp: datetime
    kind: str = ""  # whale_movement | exchange_inflow | exchange_outflow
    source: str = ""


class OnChainMetrics(BaseModel):
    asset: str
    btc_fee_estimate: dict | None = None
    mempool_size: int | None = None
    active_addresses: float | None = None
    exchange_inflow_24h: float | None = None
    exchange_outflow_24h: float | None = None
    whale_transactions: list[WhaleTransaction] = Field(default_factory=list)
    source: str = ""
