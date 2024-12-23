"""Process different types of feeds and aggregate their content."""
from typing import List, Dict, Tuple
from api.models.feed_item import FeedItem

# Import all connectors
from .connectors.web import WebConnector
from .connectors.rss import RSSConnector
from .connectors.youtube import YouTubeConnector
from .connectors.gmail import GmailConnector
from .connectors.file import FileConnector
from .connectors.youtube_channel import YouTubeChannelConnector

# List of available connectors
FEED_CONNECTORS = [
    WebConnector,
    RSSConnector, 
    YouTubeConnector,
    YouTubeChannelConnector,
    GmailConnector,
    FileConnector
]

def process_feeds(feed_urls: List[str]) -> Tuple[List[Dict[str, str]], List[FeedItem]]:
    """
    Process a list of feed URLs and return their content and feed items.
    
    Args:
        feed_urls: List of URLs to process
        
    Returns:
        Tuple of (content_list, feed_items)
    """
    all_content = []
    feed_items = []
    
    for url in feed_urls:
        # Find first connector that can handle this URL
        for connector in FEED_CONNECTORS:
            if connector.can_handle(url):
                contents = connector.fetch_content(url)
                
                # Process results
                for content in contents:
                    all_content.append(content)
                    feed_items.append(FeedItem.create(
                        url=content['url'],
                        content=content['content']
                    ))
                
    return all_content, feed_items