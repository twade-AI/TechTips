"""
Curated Newsfeed — RSS aggregator for education innovation articles.

Pulls articles from configurable education/edtech RSS feeds.
"""

import feedparser
import httpx


async def fetch_feed(url: str, limit: int = 10) -> list[dict]:
    """Fetch and parse an RSS feed, returning structured entries."""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as http:
            response = await http.get(url)
            feed = feedparser.parse(response.text)
    except Exception:
        return []

    articles = []
    for entry in feed.entries[:limit]:
        published = ""
        if hasattr(entry, "published"):
            published = entry.published
        elif hasattr(entry, "updated"):
            published = entry.updated

        articles.append({
            "title": entry.get("title", "Untitled"),
            "url": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "published": published,
            "source": feed.feed.get("title", "Unknown"),
        })
    return articles


async def fetch_all_feeds(feeds: list[dict], limit_per_feed: int = 5) -> list[dict]:
    """Fetch articles from all active feed sources."""
    all_articles = []
    for feed in feeds:
        articles = await fetch_feed(feed["url"], limit=limit_per_feed)
        for article in articles:
            article["category"] = feed.get("category", "general")
            article["source_name"] = feed.get("name", article["source"])
        all_articles.extend(articles)
    return all_articles
