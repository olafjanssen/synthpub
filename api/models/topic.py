"""Topic model definitions."""
from pydantic import BaseModel
from typing import List

class TopicCreate(BaseModel):
    """Data required to create a new topic."""
    name: str
    description: str
    feed_urls: List[str] = []  # Default to empty list if not provided

class Topic(TopicCreate):
    """Topic model with all fields."""
    id: str
    article: str  # ID of the associated article