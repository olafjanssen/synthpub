"""
RSS connector for fetching links from RSS feeds.
"""
import ssl
import feedparser
from typing import List, Dict
from datetime import datetime

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
    
    entries = []
    for entry in feed.entries:
        entries.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.get('published', ''),
        })
    
    return entries