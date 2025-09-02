"""Base interface for converters."""

from typing import Protocol

from typing_extensions import runtime_checkable

from api.db import article_db
from api.models import Article
from utils.logging import debug, error
from utils.rate_limit_utils import RateLimitError, is_rate_limit_error


@runtime_checkable
class Converter(Protocol):
    """Protocol for converters."""

    @staticmethod
    def can_handle(content_type: str) -> bool:
        """Check if this converter can handle the given type."""
        ...

    @staticmethod
    def convert_representation(content_type: str, article: Article) -> bool:
        """
        Convert article to the specified representation format.

        Args:
            content_type: The type to convert to
            article: The article to convert

        Returns:
            bool: True if conversion succeeded
        """
        ...

    @classmethod
    def handle_convert_requested(cls, sender: Article, content_type: str):
        """Handle conversion request signal."""
        if cls.can_handle(content_type):
            debug(
                "CONVERT",
                "Using handler",
                f"Type: {content_type}, Handler: {cls.__name__}",
            )
            try:
                cls.convert_representation(content_type, sender)
                article_db.save_article(sender)
            except Exception as e:
                # Check if this is a rate limit error and re-raise it
                if is_rate_limit_error(e):
                    error(
                        "CONVERT",
                        "Rate limit error",
                        f"Type: {content_type}, Error: {str(e)}",
                    )
                    raise RateLimitError(
                        f"Rate limit error in converter {cls.__name__}: {str(e)}",
                        original_exception=e,
                    )
                else:
                    error("CONVERT", "Failed", f"Type: {content_type}, Error: {str(e)}")
