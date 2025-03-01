"""Topic-related data models."""
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from .feed_item import FeedItem

class TopicBase(BaseModel):
    """Base topic model."""
    name: str
    description: str
    feed_urls: List[str]
    publish_urls: List[str] = []

class TopicCreate(TopicBase):
    """Topic creation model."""
    pass

class TopicUpdate(BaseModel):
    """Topic update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    feed_urls: Optional[List[str]] = None
    publish_urls: Optional[List[str]] = None

class Representation(BaseModel):
    """Model for content representations."""
    type: str
    content: str
    created_at: datetime = datetime.now()
    metadata: Dict = {}

class Topic(TopicBase):
    """Complete topic model."""
    id: str
    article: Optional[str] = None
    representations: List[Representation] = []
    processed_feeds: List[FeedItem] = []
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None

    def add_representation(self, type: str, content: str, metadata: Dict = {}) -> None:
        """Add a new representation to the topic."""
        self.representations.append(
            Representation(
                type=type,
                content=content,
                metadata=metadata
            )
        )
