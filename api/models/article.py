"""Article model definitions."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Article(BaseModel):
    """Article model with metadata and content."""
    id: str
    title: str
    topic_id: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    version: int = 1 