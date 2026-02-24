"""
Curated Newsfeed — RSS aggregator with AI-powered summaries.

Pulls articles from configurable education/edtech RSS feeds,
generates concise summaries, and tags by relevance.
"""

import os
import json
import feedparser
import httpx
from anthropic import AsyncAnthropic
from datetime import datetime

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


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


async def summarise_article(title: str, content: str) -> dict:
    """Use Claude to generate a concise summary and relevance tags."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {
            "summary": content[:300] + "..." if len(content) > 300 else content,
            "tags": ["education"],
            "relevance_score": 5,
        }

    try:
        message = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system="You summarise education articles for UK teachers and school leaders interested in innovation for 11-18 year olds. Respond with JSON only, no markdown.",
            messages=[{
                "role": "user",
                "content": f"""Summarise this article and tag it.

Title: {title}
Content: {content[:2000]}

Respond as JSON:
{{
  "summary": "2-3 sentence summary focused on relevance to UK secondary education",
  "tags": ["up to 5 relevant tags from: pedagogy, edtech, assessment, curriculum, policy, AI, enterprise, employability, wellbeing, inclusion, leadership, CPD"],
  "relevance_score": "1-10 rating of relevance to education innovation for 11-18 year olds"
}}"""
            }],
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        return json.loads(raw)
    except Exception:
        return {
            "summary": content[:300] + "..." if len(content) > 300 else content,
            "tags": ["education"],
            "relevance_score": 5,
        }
