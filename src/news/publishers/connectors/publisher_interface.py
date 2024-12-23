"""Base interface for publishers."""
from typing import Dict, Protocol
from typing_extensions import runtime_checkable

@runtime_checkable
class Publisher(Protocol):
    """Protocol for publishers."""
    
    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this publisher can handle the given URL."""
        ...
        
    @staticmethod
    def publish_content(url: str, content: Dict[str, str]) -> bool:
        """
        Publish content to the given URL.
        
        Args:
            url: The destination URL (e.g., file://path/to/file.md)
            content: Dict containing at least 'title' and 'content' keys
            
        Returns:
            bool: True if publishing succeeded
        """
        ... 