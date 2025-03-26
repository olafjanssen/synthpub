"""Publisher interface for publishing content."""

from typing import Protocol

from typing_extensions import runtime_checkable

from api.models import Article
from utils.logging import debug, error


@runtime_checkable
class Publisher(Protocol):
    """Protocol for publishers."""

    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this publisher can handle the given URL."""
        ...

    @staticmethod
    def publish_content(url: str, article: Article) -> bool:
        """
        Publish content to the given URL.

        Args:
            url: The destination URL (e.g., file://path/to/file.md)
            article: The article to publish

        Returns:
            bool: True if publishing succeeded
        """
        ...

    @classmethod
    def handle_publish_requested(cls, sender: Article, publish_url: str):
        """Handle feed update request signal."""
        if cls.can_handle(publish_url):
            debug(
                "PUBLISH",
                "Using handler",
                f"URL: {publish_url}, Handler: {cls.__name__}",
            )
            try:
                cls.publish_content(publish_url, sender)
            except Exception as e:
                error("PUBLISH", "Failed", f"URL: {publish_url}, Error: {str(e)}")
