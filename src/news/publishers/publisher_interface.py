"""Base interface for publishers."""
from typing import Dict, Protocol
from typing_extensions import runtime_checkable
from api.signals import topic_published, publish_requested
from api.models import Topic

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
        print(f"Trying handling publish request for {publish_url} as {cls.__name__}")
        if cls.can_handle(publish_url):
            print(f"Can handle publish request for {publish_url} as {cls.__name__}")
            try:
                cls.publish_content(publish_url, sender)
                topic_published.send(sender, publish_url=publish_url)
            except Exception as e:
                print(f"Error publishing {publish_url}: {str(e)}")

    @classmethod
    def connect_signals(cls):
        """Connect to feed update signals."""
        publish_requested.connect(cls.handle_publish_requested) 