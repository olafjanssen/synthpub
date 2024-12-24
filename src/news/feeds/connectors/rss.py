"""
RSS connector for fetching links from RSS feeds.
"""
import ssl
import feedparser
from typing import List, Dict
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
from .feed_connector import FeedConnector
from api.signals import news_feed_update_requested, news_feed_item_found

def get_pub_date(entry) -> datetime:
    """Extract publication date from entry, handling multiple formats."""
    # Try different date fields
    date_field = (
        getattr(entry, 'published', None) or 
        getattr(entry, 'pubDate', None) or 
        getattr(entry, 'updated', None)
    )
    
    if not date_field:
        return datetime.min
        
    try:
        # Try email/RSS format parsing first
        return parsedate_to_datetime(date_field)
    except (TypeError, ValueError):
        # Fallback formats to try
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',  # RFC 822
            '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601
            '%Y-%m-%dT%H:%M:%SZ',        # ISO 8601 UTC
            '%a, %d %b %Y %H:%M:%S %Z',  # Alternative RFC 822
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
    # Disable SSL verification
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
        
    feed = feedparser.parse(url)
    
    entries = feed.entries
    
    # Sort entries by published date (oldest to newest)
    sorted_entries = sorted(entries, key=get_pub_date)
    
    return sorted_entries

class RSSConnector(FeedConnector):
    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and (
            url.endswith('.xml') or 
            url.endswith('.rss') or 
            'feed' in url.lower()
        )
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, str]]:
        try:
            entries = fetch_rss_links(url)
            return [{
                'url': entry.get('link', ''),
                'content': f"{entry.get('title', '')}\n\n{entry.get('summary', '')}",
                'title': entry.get('title', '')
            } for entry in entries]
        except Exception as e:
            print(f"Error fetching RSS feed {url}: {str(e)}")
            return []

RSSConnector.connect_signals()