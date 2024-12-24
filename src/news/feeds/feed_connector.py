"""Base interface for feed connectors."""
from typing import List, Dict, Protocol
from typing_extensions import runtime_checkable
from api.signals import news_feed_update_requested, news_feed_item_found
from api.models.feed_item import FeedItem
@runtime_checkable
class FeedConnector(Protocol):
    """Protocol for feed connectors."""
    
    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this connector can handle the given URL."""
        ...
        
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, str]]:
        """
        Fetch content from the given URL.
        
        Returns:
            List of dicts with at least 'url' and 'content' keys
        """
        ...

    @classmethod
    def handle_feed_update(cls, sender, feed_url: str):
        """Handle feed update request signal."""
        if cls.can_handle(feed_url):
            try:
                items = cls.fetch_content(feed_url)
                for item in items:
                    feed_item = FeedItem.create(
                        url=item['url'],
                        content=item['content']
                    )
                    news_feed_item_found.send(sender, feed_url=feed_url, feed_item=feed_item, content=item['content'])
            except Exception as e:
                print(f"Error processing feed {feed_url}: {str(e)}")

    @classmethod
    def connect_signals(cls):
        """Connect to feed update signals."""
        news_feed_update_requested.connect(cls.handle_feed_update) 