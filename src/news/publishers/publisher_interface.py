"""Publisher interface for publishing content."""

from typing import Protocol

from typing_extensions import runtime_checkable

from api.models import Article
from utils.logging import debug, error
from utils.rate_limit_utils import RateLimitError, is_rate_limit_error


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
                # Check if this is a rate limit error and re-raise it
                if is_rate_limit_error(e):
                    error("PUBLISH", "Rate limit error", f"URL: {publish_url}, Error: {str(e)}")
                    raise RateLimitError(f"Rate limit error in publisher {cls.__name__}: {str(e)}", original_exception=e)
                else:
                    error("PUBLISH", "Failed", f"URL: {publish_url}, Error: {str(e)}")
