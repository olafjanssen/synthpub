"""Topic-related data models."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .feed_item import FeedItem

class TopicBase(BaseModel):
    """Base topic model."""
    name: str
    description: str
    feed_urls: List[str]

class TopicCreate(TopicBase):
    """Topic creation model."""
    pass

class TopicUpdate(BaseModel):
    """Topic update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    feed_urls: Optional[List[str]] = None

class Topic(TopicBase):
    """Complete topic model."""
    id: str
    article: Optional[str] = None
    processed_feeds: List[FeedItem] = []
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None