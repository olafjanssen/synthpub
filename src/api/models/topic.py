"""Topic-related data models."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .feed_item import FeedItem


class TopicBase(BaseModel):
    """Base topic model."""

    name: str = Field(description="Name of the topic")
    description: str = Field(description="Detailed description of the topic")
    feed_urls: List[str] = Field(description="List of URLs to generate content from")
    publish_urls: List[str] = Field(
        default=[],
        description="List of destination URLs where the content will be published",
    )
    thumbnail_url: Optional[str] = Field(
        default=None,
        description="URL of the thumbnail image, can be auto-generated if not provided",
    )
    slug: Optional[str] = Field(
        default=None,
        description="URL-friendly version of the name for use in paths",
    )


class TopicCreate(TopicBase):
    """Topic creation model."""


class TopicUpdate(BaseModel):
    """Topic update model."""

    name: Optional[str] = Field(default=None, description="Updated name of the topic")
    description: Optional[str] = Field(
        default=None, description="Updated description of the topic"
    )
    feed_urls: Optional[List[str]] = Field(
        default=None, description="Updated list of RSS/Atom feed URLs"
    )
    publish_urls: Optional[List[str]] = Field(
        default=None, description="Updated list of destination URLs for publishing"
    )
    thumbnail_url: Optional[str] = Field(
        default=None,
        description="Updated thumbnail URL, use 'auto' for automatic generation",
    )
    slug: Optional[str] = Field(
        default=None,
        description="Updated URL-friendly version of the name",
    )


class Representation(BaseModel):
    """Model for content representations."""

    type: str = Field(description="Type of representation (e.g., 'markdown', 'html')")
    content: str = Field(description="Content of this representation")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when this representation was created",
    )
    metadata: Dict = Field(
        default={},
        description="Additional metadata associated with this representation",
    )


class Topic(TopicBase):
    """Complete topic model."""

    id: str = Field(description="Unique identifier for the topic")
    article: Optional[str] = Field(
        default=None,
        description="ID of the associated article, if one has been generated",
    )
    representations: List[Representation] = Field(
        default=[], description="Different content representations of this topic"
    )
    processed_feeds: List[FeedItem] = Field(
        default=[], description="Feed items that have been processed for this topic"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when this topic was created",
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Timestamp when this topic was last updated"
    )

    def __init__(self, **data):
        """Initialize a topic."""
        super().__init__(**data)
        self.processed_feeds = self.processed_feeds or []

    def add_representation(
        self, content_type: str, content: str, metadata: Optional[Dict] = None
    ) -> None:
        """Add a new representation to the topic."""
        if metadata is None:
            metadata = {}
        self.representations.append(
            Representation(type=content_type, content=content, metadata=metadata)
        )
