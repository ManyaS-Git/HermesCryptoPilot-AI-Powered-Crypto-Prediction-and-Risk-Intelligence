"""Symbol normalization helpers shared across providers.

Users type short tickers (BTC, ETH, SOL); each exchange needs its own
naming convention. Known assets use a curated mapping; unknown symbols fall
back to a generic ``{SYMBOL}USDT`` convention.
"""
from __future__ import annotations

from app.core.config import get_settings

# Hardcoded mappings are a *presentation* concern (exchange symbol formats),
# not fabricated market data. They map one real symbol to another.
COINGECKO_IDS: dict[str, str] = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "DOT": "polkadot",
    "MATIC": "matic-network",
    "LTC": "litecoin",
    "TRX": "tron",
    "UNI": "uniswap",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "NEAR": "near",
    "SUI": "sui",
    "AAVE": "aave",
    "SHIB": "shiba-inu",
    "PEPE": "pepe",
    "INJ": "injective-protocol",
    "TIA": "celestia",
    "TON": "the-open-network",
}

# Kraken uses legacy pairs for majors
KRAKEN_PAIRS: dict[str, str] = {
    "BTC": "XBT/USD",
    "ETH": "ETH/USD",
    "SOL": "SOL/USD",
    "XRP": "XRP/USD",
    "ADA": "ADA/USD",
    "DOT": "DOT/USD",
    "LTC": "LTC/USD",
    "DOGE": "DOGE/USD",
    "LINK": "LINK/USD",
    "AVAX": "AVAX/USD",
}

ASSET_NAMES: dict[str, str] = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "SOL": "Solana",
    "BNB": "BNB",
    "XRP": "XRP",
    "ADA": "Cardano",
    "DOGE": "Dogecoin",
    "AVAX": "Avalanche",
    "LINK": "Chainlink",
    "DOT": "Polkadot",
    "MATIC": "Polygon",
    "LTC": "Litecoin",
    "TRX": "TRON",
    "UNI": "Uniswap",
    "APT": "Aptos",
    "ARB": "Arbitrum",
    "OP": "Optimism",
    "NEAR": "NEAR Protocol",
    "SUI": "Sui",
    "AAVE": "Aave",
    "SHIB": "Shiba Inu",
    "PEPE": "Pepe",
    "INJ": "Injective",
    "TIA": "Celestia",
    "TON": "Toncoin",
}


def normalize_asset(asset: str) -> str:
    return asset.strip().upper()


def usdt_pair(asset: str) -> str:
    return f"{normalize_asset(asset)}{get_settings().DEFAULT_QUOTE}"


def coingecko_id(asset: str) -> str:
    return COINGECKO_IDS.get(normalize_asset(asset), normalize_asset(asset).lower())


def kraken_pair(asset: str) -> str:
    return KRAKEN_PAIRS.get(normalize_asset(asset), f"{normalize_asset(asset)}/USD")


def asset_name(asset: str) -> str:
    return ASSET_NAMES.get(normalize_asset(asset), normalize_asset(asset))
