"""Feed item model definitions."""
from pydantic import BaseModel
from datetime import datetime
import hashlib

class FeedItem(BaseModel):
    """Model for processed feed items."""
    url: str
    accessed_at: datetime
    content_hash: str
    is_relevant: bool = False
    needs_further_processing: bool = False

    @classmethod
    def create(cls, url: str, content: str, needs_further_processing: bool = False) -> "FeedItem":
        """
        Create a new feed item with computed hash.
        
        Args:
            url: URL of the feed item
            content: Content of the feed item
            needs_further_processing: Whether this item needs to be processed by another connector
        """
        return cls(
            url=url,
            accessed_at=datetime.utcnow(),
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
            needs_further_processing=needs_further_processing
        ) 