from __future__ import annotations

from typing import List

import feedparser


class NewsService:
    def __init__(self, rss_url: str, limit: int = 5) -> None:
        self.rss_url = rss_url
        self.limit = limit

    def fetch_headlines(self) -> List[str]:
        try:
            feed = feedparser.parse(self.rss_url)
            titles = [entry.get("title", "") for entry in feed.entries]
            titles = [t.strip() for t in titles if t and isinstance(t, str)]
            return titles[: self.limit]
        except Exception:
            return []


