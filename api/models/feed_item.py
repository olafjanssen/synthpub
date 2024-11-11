"""Feed item model definitions."""
from pydantic import BaseModel
from datetime import datetime
import hashlib

class FeedItem(BaseModel):
    """Model for processed feed items."""
    url: str
    accessed_at: datetime
    content_hash: str

    @classmethod
    def create(cls, url: str, content: str) -> "FeedItem":
        """Create a new feed item with computed hash."""
        return cls(
            url=url,
            accessed_at=datetime.utcnow(),
            content_hash=hashlib.sha256(content.encode()).hexdigest()
        ) 