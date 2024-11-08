"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel

class TopicCreate(BaseModel):
    """Request model for creating a topic."""
    name: str
    description: str

class Topic(BaseModel):
    """Response model for a topic."""
    name: str
    description: str
    article: str | None = None 