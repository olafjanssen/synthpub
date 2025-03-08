"""Publisher interface for publishing content."""
from typing import Dict, Protocol
from typing_extensions import runtime_checkable
from api.signals import topic_published, publish_requested
from api.models import Topic
from utils.logging import debug, info, error

@runtime_checkable
class Publisher(Protocol):
    """Protocol for publishers."""
    
    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this publisher can handle the given URL."""
        ...
        
    @staticmethod
    def publish_content(url: str, topic: Topic) -> bool:
        """
        Publish content to the given URL.
        
        Args:
            url: The destination URL (e.g., file://path/to/file.md)
            topic: The topic to publish
            
        Returns:
            bool: True if publishing succeeded
        """
        ... 

    @classmethod
    def handle_publish_requested(cls, sender, publish_url: str):
        """Handle feed update request signal."""
        debug("PUBLISH", "Checking handler", f"URL: {publish_url}, Handler: {cls.__name__}")
        if cls.can_handle(publish_url):
            debug("PUBLISH", "Using handler", f"URL: {publish_url}, Handler: {cls.__name__}")
            try:
                cls.publish_content(publish_url, sender)
                topic_published.send(sender, publish_url=publish_url)
            except Exception as e:
                error("PUBLISH", "Failed", f"URL: {publish_url}, Error: {str(e)}")

    @classmethod
    def connect_signals(cls):
        """Connect to feed update signals."""
        publish_requested.connect(cls.handle_publish_requested) 