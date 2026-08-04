"""Sentiment intelligence: scores news articles per asset using VADER.

Entity extraction maps asset symbols/names mentioned in headlines, then
aggregates a weighted sentiment score for each asset over a lookback window.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.core.cache import get_cache
from app.domain.news import NewsArticle, SentimentResult
from app.services.intelligence.news import NewsService
from app.services.market.symbols import ASSET_NAMES

_analyzer = SentimentIntensityAnalyzer()

# Signal words boost detection for crypto context
_EXTRA_TERMS = {
    "btc": "BTC", "bitcoin": "BTC", "xbt": "BTC",
    "eth": "ETH", "ethereum": "ETH", "ether": "ETH",
    "sol": "SOL", "solana": "SOL",
    "bnb": "BNB", "binance coin": "BNB",
    "xrp": "XRP", "ripple": "XRP",
    "ada": "ADA", "cardano": "ADA",
    "doge": "DOGE", "dogecoin": "DOGE",
    "avax": "AVAX", "avalanche": "AVAX",
    "link": "LINK", "chainlink": "LINK",
    "dot": "DOT", "polkadot": "DOT",
    "matic": "MATIC", "polygon": "MATIC",
    "ltc": "LTC", "litecoin": "LTC",
    "arb": "ARB", "arbitrum": "ARB",
    "op": "OP", "optimism": "OP",
    "apt": "APT", "aptos": "APT",
    "sui": "SUI", "shib": "SHIB", "pepe": "PEPE",
    "ton": "TON", "toncoin": "TON", "injective": "INJ", "tia": "TIA", "celestia": "TIA",
}


def extract_entities(text: str) -> list[str]:
    lowered = text.lower()
    found: set[str] = set()
    for key, asset in _EXTRA_TERMS.items():
        if key in lowered:
            found.add(asset)
    return sorted(found)


def score_text(text: str) -> tuple[float, float]:
    """Return (compound score, magnitude) via VADER."""
    sentiment = _analyzer.polarity_scores(text)
    return float(sentiment["compound"]), float(abs(sentiment["compound"]))


def label_for(score: float) -> str:
    if score > 0.15:
        return "bullish"
    if score < -0.15:
        return "bearish"
    return "neutral"


class SentimentService:
    def __init__(self) -> None:
        self.news = NewsService()
        self.cache = get_cache()

    async def analyze(self, asset: str, hours: int = 24, limit: int = 100) -> SentimentResult:
        cache_key = f"sentiment:{asset.upper()}:{hours}"
        cached = await self.cache.get(cache_key)
        if cached:
            return SentimentResult.model_validate(cached)

        articles = await self.news.fetch_news(limit=max(limit, 60))
        window_start = datetime.now(timezone.utc) - timedelta(hours=hours)
        relevant: list[NewsArticle] = []
        for article in articles:
            entities = extract_entities(article.title)
            if asset.upper() in entities or asset.lower() in article.title.lower():
                if article.published_at >= window_start:
                    relevant.append(article)

        if not relevant:
            result = SentimentResult(
                asset=asset.upper(),
                score=0.0,
                magnitude=0.0,
                label="neutral",
                article_count=0,
                sources=[],
                window_start=window_start,
                window_end=datetime.now(timezone.utc),
            )
        else:
            scores = [score_text(f"{a.title}. {a.summary}") for a in relevant]
            weights = [1.0 + 0.5 * m for _, m in scores]
            total_weight = sum(weights)
            weighted_score = sum(c * w for (c, _), w in zip(scores, weights)) / total_weight
            result = SentimentResult(
                asset=asset.upper(),
                score=round(weighted_score, 4),
                magnitude=round(sum(w for _, w in scores) / len(scores), 4),
                label=label_for(weighted_score),
                article_count=len(relevant),
                sources=sorted({a.source for a in relevant}),
                window_start=window_start,
                window_end=datetime.now(timezone.utc),
            )

        await self.cache.set(cache_key, result.model_dump(), ttl=180)
        return result
