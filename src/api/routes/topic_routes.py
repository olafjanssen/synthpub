"""Topic-related API routes."""
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from api.models.topic import Topic, TopicCreate, TopicUpdate
from api.db.topic_db import load_topics, mark_topic_deleted, update_topic, get_topic, save_topic
from api.db.article_db import create_article
from curator.article_generator import generate_article
from typing import List
from curator.topic_updater import update_topic
from api.signals import topic_update_requested

router = APIRouter()

@router.post("/topics/", response_model=Topic)
async def create_topic_route(topic: TopicCreate):
    """Create a new topic and generate its initial article."""
    try:
        topic_id = str(uuid4())
        
        # Create topic and initial article
        content = generate_article(topic.description)
            
        article = create_article(
            title=topic.name,
            topic_id=topic_id,
            content=content
        )
        
        topic_data = Topic(
            id=topic_id,
            name=topic.name,
            description=topic.description,
            article=article.id,
            feed_urls=topic.feed_urls
        )
            
        # Save to database
        save_topic(topic_data)
        
        return topic_data
        
    except Exception as e:
        print(f"Error creating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/topics/", response_model=list[Topic])
async def list_topics_route():
    """List all topics."""
    topics = load_topics()
    return list(topics.values())

@router.get("/topics/{topic_id}", response_model=Topic)
async def get_topic_route(topic_id: str):
    """Get a specific topic by ID."""
    topics = load_topics()
    if topic_id not in topics:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topics[topic_id]

# Add a new route to update feed URLs
@router.put("/topics/{topic_id}/feeds", response_model=Topic)
async def update_topic_feeds_route(topic_id: str, feed_urls: List[str]):
    """Update the feed URLs for a specific topic."""
    topics = load_topics()
    if topic_id not in topics:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic = get_topic(topic_id)
    topic.feed_urls = feed_urls
    save_topic(topic)
    
    return topic

@router.post("/topics/{topic_id}/update", response_model=dict)
async def update_topic_route(topic_id: str):
    """Request topic update via signal."""
    # Send signal instead of directly spawning thread
    print(f"Sending signal for topic {topic_id}")
    topic_update_requested.send('api', topic_id=topic_id)
    return {"message": "Topic update requested", "topic_id": topic_id}

@router.delete("/topics/{topic_id}", response_model=dict)
async def delete_topic_route(topic_id: str):
    """Mark a topic as deleted (soft delete)."""
    try:
        # Check if topic exists
        topics = load_topics()
        if topic_id not in topics:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Mark topic as deleted
        success = mark_topic_deleted(topic_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete topic")
        
        return {"message": "Topic marked as deleted", "topic_id": topic_id}
        
    except Exception as e:
        print(f"Error deleting topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/topics/{topic_id}", response_model=Topic)
async def update_topic_route(topic_id: str, topic_update: TopicUpdate):
    """Update a topic's details."""
    try:
        # Check if topic exists
        topics = load_topics()
        if topic_id not in topics:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Update topic
        updated_topic = update_topic(topic_id, topic_update.model_dump(exclude_unset=True))
        if not updated_topic:
            raise HTTPException(status_code=500, detail="Failed to update topic")
        
        return updated_topic
        
    except Exception as e:
        print(f"Error updating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")