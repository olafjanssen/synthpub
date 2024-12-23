"""Base interface for feed connectors."""
from typing import List, Dict, Protocol
from typing_extensions import runtime_checkable

@runtime_checkable
class FeedConnector(Protocol):
    """Protocol for feed connectors."""
    
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
        """
        ... 