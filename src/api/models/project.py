"""Project-related data models."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectBase(BaseModel):
    """Base project model."""
    title: str
    description: str
    topic_ids: List[str] = []

class ProjectCreate(ProjectBase):
    """Project creation model."""
    pass

class ProjectUpdate(BaseModel):
    """Project update model."""
    title: Optional[str] = None
    description: Optional[str] = None
    topic_ids: Optional[List[str]] = None

class Project(ProjectBase):
    """Complete project model."""
    id: str
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None 