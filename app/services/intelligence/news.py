"""News intelligence: aggregates real crypto news from multiple sources.

Source order: CryptoPanic API (if key configured) -> free RSS feeds
(CoinDesk, CoinTelegraph, Cointelegraph). Results are cached and persisted
to the database when a session is available.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from app.core.cache import get_cache
from app.core.config import get_settings
from app.domain.news import NewsArticle
from app.services.market.clients import provider_get

RSS_FEEDS = [
    ("coindesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("cointelegraph", "https://cointelegraph.com/rss"),
    ("decrypt", "https://decrypt.co/feed"),
]

MAX_ARTICLES = 60


def _parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return datetime.now(timezone.utc)


def _parse_rss(xml_text: str, source: str) -> list[NewsArticle]:
    articles: list[NewsArticle] = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            if not title or not link:
                continue
            published = item.findtext("pubDate") or item.findtext("dc:date")
            summary = (item.findtext("description") or "")[:500]
            articles.append(
                NewsArticle(
                    title=title,
                    url=link,
                    source=source,
                    published_at=_parse_datetime(published) if published else datetime.now(timezone.utc),
                    summary=summary,
                )
            )
            if len(articles) >= MAX_ARTICLES:
                break
    except ET.ParseError:
        return []
    return articles


class NewsService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = get_cache()

    async def fetch_news(self, limit: int = 30, category: str = "all") -> list[NewsArticle]:
        cache_key = f"news:feed:{category}:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return [NewsArticle.model_validate(a) for a in cached]

        articles: list[NewsArticle] = []

        # CryptoPanic (requires API key)
        if self.settings.CRYPTOPANIC_API_KEY:
            try:
                params = {"auth_token": self.settings.CRYPTOPANIC_API_KEY}
                if category != "all":
                    params["categories"] = category
                resp = await provider_get(
                    "https://cryptopanic.com/api/v1/posts/",
                    params=params,
                    provider="cryptopanic",
                    rps=5,
                )
                for post in resp.json().get("results", []):
                    articles.append(
                        NewsArticle(
                            title=post.get("title", ""),
                            url=post.get("url", ""),
                            source="cryptopanic",
                            published_at=_parse_datetime(post.get("published_at", "")),
                            summary="",
                            category=post.get("kind", "general"),
                        )
                    )
            except Exception:
                pass

        # RSS fallbacks / supplement
        if len(articles) < limit:
            for source, url in RSS_FEEDS:
                try:
                    resp = await provider_get(url, provider="rss", rps=3)
                    articles.extend(_parse_rss(resp.text, source))
                except Exception:
                    continue

        # Dedupe by url, sort by recency
        seen: set[str] = set()
        unique: list[NewsArticle] = []
        for a in articles:
            if a.url in seen:
                continue
            seen.add(a.url)
            unique.append(a)
        unique.sort(key=lambda a: a.published_at, reverse=True)

        result = unique[:limit]
        await self.cache.set(cache_key, [a.model_dump() for a in result], ttl=120)
        return result
