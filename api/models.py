"""
Pydantic models for the API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TopicCreate(BaseModel):
    """Model for creating a new topic."""
    name: str
    description: str

class Topic(TopicCreate):
    """Model for a topic with generated article."""
    id: str
    article: str

class Article(BaseModel):
    """Article model with metadata and content."""
    id: str
    title: str
    topic_id: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    version: int = 1