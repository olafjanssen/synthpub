"""Project-related data models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project model."""

    title: str = Field(description="Title of the project")
    description: str = Field(description="Detailed description of the project")
    topic_ids: List[str] = Field(
        default=[], description="List of topic IDs associated with this project"
    )
    thumbnail_url: Optional[str] = Field(
        default=None,
        description="URL of the thumbnail image, can be auto-generated if not provided",
    )
    slug: Optional[str] = Field(
        default=None,
        description="URL-friendly version of the title for use in paths",
    )


class ProjectCreate(ProjectBase):
    """Project creation model."""


class ProjectUpdate(BaseModel):
    """Project update model."""

    title: Optional[str] = Field(
        default=None, description="Updated title of the project"
    )
    description: Optional[str] = Field(
        default=None, description="Updated description of the project"
    )
    topic_ids: Optional[List[str]] = Field(
        default=None, description="Updated list of topic IDs"
    )
    thumbnail_url: Optional[str] = Field(
        default=None,
        description="Updated thumbnail URL, use 'auto' for automatic generation",
    )
    slug: Optional[str] = Field(
        default=None,
        description="Updated URL-friendly version of the title",
    )


class Project(ProjectBase):
    """Complete project model."""

    id: str = Field(description="Unique identifier for the project")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when this project was created",
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Timestamp when this project was last updated"
    )
