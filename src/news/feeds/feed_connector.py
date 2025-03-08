"""Base interface for feed connectors."""
from typing import List, Dict, Protocol
from typing_extensions import runtime_checkable
from api.signals import news_feed_update_requested, news_feed_item_found
from api.models.feed_item import FeedItem
from api.db.cache_manager import get_from_cache, add_to_cache
from utils.logging import debug, info, error, warning

@runtime_checkable
class FeedConnector(Protocol):
    """Protocol for feed connectors."""
    
    # Cache expiration time in seconds
    # -1: cache forever (default)
    # 0: never cache
    # >0: seconds to cache
    cache_expiration: int = -1
    
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
            Additional optional keys:
            - needs_further_processing: bool - Whether this item needs to be processed by another connector
        """
        ...

    @classmethod
    def handle_feed_update(cls, sender, feed_url: str):
        """
        Handle feed update request signal.
        
        This method processes the feed URL and either:
        1. For items needing further processing (like RSS entries or playlist videos):
           - Sends a new feed_update_requested signal for each item URL
        2. For final content items (like web pages or individual files):
           - Creates FeedItem objects and sends them for processing
        """
        debug("FEED", "Checking handler", f"URL: {feed_url}, Handler: {cls.__name__}")
        if cls.can_handle(feed_url):
            info("FEED", "Using handler", f"URL: {feed_url}, Handler: {cls.__name__}")
            try:
                # Check cache first
                cached_data = get_from_cache(feed_url)
                if cached_data and isinstance(cached_data, dict) and 'items' in cached_data:
                    debug("FEED", "Using cached data", feed_url)
                    items = cached_data['items']
                else:
                    # Fetch fresh content
                    items = cls.fetch_content(feed_url)
                    info("FEED", "Content fetched", f"Items: {len(items)}, URL: {feed_url}")
                    
                    # Cache the results if caching is enabled
                    if cls.cache_expiration != 0 and items:
                        add_to_cache(feed_url, {'items': items}, cls.cache_expiration)
                
                # Process each item according to its needs_further_processing flag
                for item in items:
                    # Check if this item needs further processing
                    needs_further_processing = item.get('needs_further_processing', False)
                    
                    if needs_further_processing:
                        # For items needing further processing, send a new update request
                        item_url = item['url']
                        debug("FEED", "Further processing needed", item_url)
                        news_feed_update_requested.send(sender, feed_url=item_url)
                    else:
                        # For final content items, create a FeedItem and send to processing queue
                        feed_item = FeedItem.create(
                            url=item['url'],
                            content=item['content'],
                            needs_further_processing=False  # Explicitly mark as not needing further processing
                        )
                        # Send signal to queue the item
                        news_feed_item_found.send(sender, feed_url=feed_url, feed_item=feed_item, content=item['content'])
                    
            except Exception as e:
                error("FEED", "Processing error", f"URL: {feed_url}, Error: {str(e)}")

    @classmethod
    def connect_signals(cls):
        """Connect to feed update signals."""
        news_feed_update_requested.connect(cls.handle_feed_update) 