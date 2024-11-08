"""Topic model definitions."""
from pydantic import BaseModel

class TopicCreate(BaseModel):
    """Data required to create a new topic."""
    name: str
    description: str

class Topic(TopicCreate):
    """Topic model with all fields."""
    id: str
    article: str  # ID of the associated article 