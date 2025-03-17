"""Topic-related data models."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from .feed_item import FeedItem


class TopicBase(BaseModel):
    """Base topic model."""

    name: str
    description: str
    feed_urls: List[str]
    publish_urls: List[str] = []
    thumbnail_url: Optional[str] = None


class TopicCreate(TopicBase):
    """Topic creation model."""


class TopicUpdate(BaseModel):
    """Topic update model."""

    name: Optional[str] = None
    description: Optional[str] = None
    feed_urls: Optional[List[str]] = None
    publish_urls: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None


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

    def __init__(self, **data):
        """Initialize a topic."""
        super().__init__(**data)
        self.processed_feeds = self.processed_feeds or []

    def add_representation(
        self, content_type: str, content: str, metadata: Dict = {}
    ) -> None:
        """Add a new representation to the topic."""
        self.representations.append(
            Representation(type=content_type, content=content, metadata=metadata)
        )
