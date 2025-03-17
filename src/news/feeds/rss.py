"""
RSS connector for fetching links from RSS feeds.
"""

import ssl
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Dict, List
from urllib.parse import urlparse

import feedparser

from utils.logging import error, info, warning

from .feed_connector import FeedConnector


def get_pub_date(entry) -> datetime:
    """Extract publication date from entry, handling multiple formats."""
    # Try different date fields
    date_field = (
        getattr(entry, "published", None)
        or getattr(entry, "pubDate", None)
        or getattr(entry, "updated", None)
    )

    if not date_field:
        return datetime.min

    try:
        # Try email/RSS format parsing first
        return parsedate_to_datetime(date_field)
    except (TypeError, ValueError):
        # Fallback formats to try
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",  # RFC 822
            "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601
            "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 UTC
            "%a, %d %b %Y %H:%M:%S %Z",  # Alternative RFC 822
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_field, fmt)
            except ValueError:
                continue

        return datetime.min


def fetch_rss_links(url: str) -> List[Dict[str, str]]:
    """
    Fetch all entries from an RSS feed and return their links.

    Args:
        url: The RSS feed URL

    Returns:
        List of dicts containing title, link, and published date
    """
    # Create a custom SSL context with verification
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    # Use the custom SSL context
    if hasattr(ssl, "_create_unverified_context"):
        ssl._create_default_https_context = lambda: ssl_context

    feed = feedparser.parse(url)

    entries = feed.entries

    # Sort entries by published date (oldest to newest)
    sorted_entries = sorted(entries, key=get_pub_date)

    return sorted_entries


class RSSConnector(FeedConnector):
    # Cache RSS feeds for 1 hour
    cache_expiration = 3600

    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https", "feed") and (
            url.endswith(".xml") or url.endswith(".rss") or "feed" in url.lower()
        )

    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, str]]:
        try:
            entries = fetch_rss_links(url)
            return [
                {
                    "url": entry.get("link", ""),
                    "content": f"{entry.get('title', '')}\n\n{entry.get('summary', '')}",
                    "title": entry.get("title", ""),
                    "needs_further_processing": True,  # Mark RSS items as needing further processing
                }
                for entry in entries
            ]
        except Exception as e:
            error("RSS", "Fetch failed", f"URL: {url}, Error: {str(e)}")
            return []
