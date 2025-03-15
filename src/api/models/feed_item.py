"""Feed item model definitions."""
from pydantic import BaseModel
from datetime import datetime, timezone
import hashlib
from typing import Optional

class FeedItem(BaseModel):
    """Model for processed feed items."""
    url: str
    accessed_at: datetime
    content_hash: str
    is_relevant: bool = False
    relevance_explanation: str = ""
    needs_further_processing: bool = False
    
    # Substance extraction information
    new_information: str = ""
    enforcing_information: str = ""
    contradicting_information: str = ""
    
    # Resulting article reference
    article_id: Optional[str] = None

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
            accessed_at=datetime.now(timezone.utc),
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
            needs_further_processing=needs_further_processing
        ) 