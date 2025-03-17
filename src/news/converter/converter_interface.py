"""Base interface for publishers."""

from typing import Protocol

from typing_extensions import runtime_checkable

from api.models import Topic
from api.signals import convert_requested
from utils.logging import debug, error


@runtime_checkable
class Converter(Protocol):
    """Protocol for converters."""

    @staticmethod
    def can_handle(content_type: str) -> bool:
        """Check if this converter can handle the given type."""
        ...

    @staticmethod
    def convert_representation(content_type: str, topic: Topic) -> bool:
        """
        Publish content to the given URL.

        Args:
            content_type: The type to convert to
            topic: The topic to convert

        Returns:
            bool: True if conversion succeeded
        """
        ...

    @classmethod
    def handle_convert_requested(cls, sender, content_type: str):
        """Handle conversion request signal."""
        debug(
            "CONVERT",
            "Checking handler",
            f"Type: {content_type}, Handler: {cls.__name__}",
        )
        if cls.can_handle(content_type):
            debug(
                "CONVERT",
                "Using handler",
                f"Type: {content_type}, Handler: {cls.__name__}",
            )
            try:
                cls.convert_representation(content_type, sender)
            except Exception as e:
                error("CONVERT", "Failed", f"Type: {content_type}, Error: {str(e)}")
        else:
            debug(
                "CONVERT",
                "No suitable handler",
                f"Type: {content_type}, Handler: {cls.__name__}",
            )

    @classmethod
    def connect_signals(cls):
        """Connect to conversion signals."""
        convert_requested.connect(cls.handle_convert_requested)
