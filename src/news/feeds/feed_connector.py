"""Base interface for feed connectors."""

from typing import Dict, List, Protocol

from typing_extensions import runtime_checkable

from api.db.cache_manager import add_to_cache, get_from_cache
from api.models.feed_item import FeedItem
from utils.logging import debug, error, info


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

    def _process_cached_items(
        self, cached_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Process cached feed items."""
        if not isinstance(cached_data, dict) or "items" not in cached_data:
            return []
        return cached_data["items"]

    def _process_feed_item(self, item: Dict[str, str], topic_id: str):
        """Process a single feed item."""
        needs_further_processing = item.get("needs_further_processing", False)
        item_url = item["url"]
        item_content = item.get("content", "")

        if needs_further_processing:
            debug("FEED", "Further processing needed", item_url)

        # Create feed item with appropriate processing flag
        feed_item = FeedItem.create(
            url=item_url,
            content=item_content,
            needs_further_processing=needs_further_processing,
        )

        # Directly add to queue with the topic's ID
        add_feed_item_to_queue(topic_id, feed_item, item_content)

    @classmethod
    def handle_feed_update(cls, topic_id: str, feed_url: str):
        """
        Handle feed update request.

        This method processes the feed URL and either:
        1. For items needing further processing (like RSS entries or playlist videos):
           - Directly processes each item URL with the appropriate connector
        2. For final content items (like web pages or individual files):
           - Creates FeedItem objects and sends them for processing

        Args:
            topic_id: The topic ID
            feed_url: The URL to process
        """
        # Import here to avoid circular imports
        from curator.topic_updater import add_feed_item_to_queue

        debug("FEED", "Checking handler", f"URL: {feed_url}, Handler: {cls.__name__}")
        if not cls.can_handle(feed_url):
            return

        debug("FEED", "Using handler", f"URL: {feed_url}, Handler: {cls.__name__}")
        try:
            # Check cache first
            cached_data = get_from_cache(feed_url)
            if cached_data:
                debug("FEED", "Using cached data", feed_url)
                items = cls._process_cached_items(cached_data)
            else:
                # Fetch fresh content
                items = cls.fetch_content(feed_url)
                info("FEED", "Content fetched", f"Items: {len(items)}, URL: {feed_url}")

            # Cache the results if caching is enabled
            if cls.cache_expiration != 0 and items:
                add_to_cache(feed_url, {"items": items}, cls.cache_expiration)

            # Process each item
            for item in items:
                cls._process_feed_item(item, topic_id)

        except Exception as e:
            error("FEED", "Processing error", f"URL: {feed_url}, Error: {str(e)}")
