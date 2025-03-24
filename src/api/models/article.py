"""Article model definitions."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .feed_item import FeedItem
from .topic import Representation


class Article(BaseModel):
    """Article model with version tracking."""

    id: str = Field(description="Unique identifier for the article")
    title: str = Field(description="Title of the article")
    topic_id: str = Field(description="ID of the parent topic this article belongs to")
    content: str = Field(description="Markdown content of the article")
    version: int = Field(
        description="Version number of this article, incremented with each update"
    )
    created_at: datetime = Field(
        description="Timestamp when this article was first created"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Timestamp when this article was last updated"
    )
    previous_version: Optional[str] = Field(
        default=None, description="ID of the previous version of this article"
    )
    next_version: Optional[str] = Field(
        default=None, description="ID of the next version of this article"
    )
    source_feed: Optional[FeedItem] = Field(
        default=None,
        description="Feed item that triggered the creation of this article version",
    )
    representations: List[Representation] = Field(
        default=[], description="Different content representations of this article"
    )

    def add_representation(
        self, content_type: str, content: str, metadata: Optional[Dict] = None
    ) -> None:
        """Add a new representation to the article."""
        if metadata is None:
            metadata = {}
        self.representations.append(
            Representation(type=content_type, content=content, metadata=metadata)
        )
