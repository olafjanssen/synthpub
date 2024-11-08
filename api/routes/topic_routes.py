"""Topic-related API routes."""
from fastapi import APIRouter, HTTPException
from ..models import Topic
from ..topic_db import create_topic, get_topic, list_topics

router = APIRouter()

@router.post("/topics", response_model=Topic)
async def create_topic_route(title: str, description: str):
    """Create a new topic."""
    try:
        topic = create_topic(
            title=title,
            description=description
        )
        return topic
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/topics/{topic_id}", response_model=Topic)
async def get_topic_route(topic_id: str):
    """Get a topic by ID."""
    topic = get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found") 