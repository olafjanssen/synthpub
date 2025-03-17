"""Project-related data models."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ProjectBase(BaseModel):
    """Base project model."""
    title: str
    description: str
    topic_ids: List[str] = []
    thumbnail_url: Optional[str] = None

class ProjectCreate(ProjectBase):
    """Project creation model."""
    pass

class ProjectUpdate(BaseModel):
    """Project update model."""
    title: Optional[str] = None
    description: Optional[str] = None
    topic_ids: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None

class Project(ProjectBase):
    """Complete project model."""
    id: str
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None 