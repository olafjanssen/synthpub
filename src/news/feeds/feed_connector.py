"""Base interface for feed connectors."""

from typing import Any, Dict, List, Protocol

from typing_extensions import runtime_checkable

from api.db.cache_manager import add_to_cache, get_from_cache
from api.models.feed_item import FeedItem
from curator.topic_updater import processing_queue
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
    def fetch_content(url: str) -> List[Dict[str, Any]]:
        """
        Fetch content from the given URL.

        Returns:
            List of dicts with at least 'url' and 'content' keys
            Additional optional keys:
            - needs_further_processing: bool - Whether this item needs to be processed by another connector
        """
        ...

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

        debug("FEED", "Checking handler", f"URL: {feed_url}, Handler: {cls.__name__}")
        if not cls.can_handle(feed_url):
            return

        debug("FEED", "Using handler", f"URL: {feed_url}, Handler: {cls.__name__}")
        try:
            # Check cache first
            cached_data = get_from_cache(feed_url)
            if cached_data:
                debug("FEED", "Using cached data", feed_url)
                items = cached_data["items"]
            else:
                # Fetch fresh content
                items = cls.fetch_content(feed_url)
                info("FEED", "Content fetched", f"Items: {len(items)}, URL: {feed_url}")

            # Cache the results if caching is enabled
            if cls.cache_expiration != 0 and items:
                add_to_cache(feed_url, {"items": items}, cls.cache_expiration)

            # Process each item
            for item in items:
                feed_item = FeedItem.create(
                    item.get("url"),
                    item.get("content", ""),
                    item.get("needs_further_processing", False),
                )
                processing_queue.put(
                    (
                        topic_id,
                        (
                            item.get("content")
                            if not feed_item.needs_further_processing
                            else None
                        ),
                        feed_item,
                    )
                )
                # process_feed_item(topic_id, item.get("url"))
                # cls._process_feed_item(item, topic_id)

        except Exception as e:
            error("FEED", "Processing error", f"URL: {feed_url}, Error: {str(e)}")
