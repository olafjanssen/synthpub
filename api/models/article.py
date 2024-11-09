"""Article model definitions."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Article(BaseModel):
    """Article model with version tracking."""
    id: str
    title: str
    topic_id: str
    content: str
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    previous_version: Optional[str] = None  # ID of the previous version