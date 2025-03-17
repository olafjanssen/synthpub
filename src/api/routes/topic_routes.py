"""Topic-related API routes."""
from typing import List
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.db.topic_db import (
    get_topic,
    load_topics,
    mark_topic_deleted,
    save_topic,
    update_topic,
)
from api.models.topic import Topic, TopicCreate, TopicUpdate
from curator.topic_updater import (
    handle_topic_publishing,
    process_feed_item,
    queue_topic_update,
)
from services.pexels_service import get_random_thumbnail
from ..db.project_db import add_topic_to_project
from utils.logging import debug, error, info

router = APIRouter()

def request_article_generation(topic_id: str):
    """Background task to request article generation."""
    process_feed_item(topic_id)

def request_topic_update(topic_id: str):
    """Background task to request topic update."""
    debug("TOPIC", "Update requested", f"ID: {topic_id}")
    queue_topic_update(topic_id)

def request_topic_publish(topic):
    """Background task to request topic publishing."""
    debug("TOPIC", "Publish requested", topic.name)
    handle_topic_publishing(topic)

@router.post("/projects/{project_id}/topics", response_model=Topic)
async def create_topic_for_project(
    project_id: str,
    topic: TopicCreate,
    background_tasks: BackgroundTasks
):
    """Create a new topic for a specific project and optionally generate an article."""
    try:
        topic_id = str(uuid4())
                

        thumbnail_url = topic.thumbnail_url
        if not thumbnail_url or thumbnail_url.lower() in ["auto", "none", ""]:
            thumbnail_data = get_random_thumbnail(f"{topic.name} {topic.description}")
            thumbnail_url = thumbnail_data.get("thumbnail_url")
        

        topic_data = Topic(
            id=topic_id,
            name=topic.name,
            description=topic.description,
            feed_urls=topic.feed_urls,
            publish_urls=topic.publish_urls,
            article=None,
            processed_feeds=[],
            thumbnail_url=thumbnail_url
        )
        
    
        save_topic(topic_data)
        info("TOPIC", "Created", topic.name)
  
        add_topic_to_project(project_id, topic_id)
        

        if topic.feed_urls:
            background_tasks.add_task(request_topic_update, topic_id)
        else:
            background_tasks.add_task(request_article_generation, topic_id)
            
        return topic_data
    except Exception as e:
        error("TOPIC", "Creation error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e

@router.get("/topics/", response_model=list[Topic])
async def list_topics_route():
    """List all topics."""
    debug("TOPIC", "List requested", "Getting all topics")
    topics = load_topics()
    return topics

@router.get("/topics/{topic_id}", response_model=Topic)
async def get_topic_route(topic_id: str):
    """Get a specific topic by ID."""
    topic = get_topic(topic_id)
    if not topic:
        error("TOPIC", "Not found", f"ID: {topic_id}")
        raise HTTPException(status_code=404, detail="Topic not found")
    debug("TOPIC", "Retrieved", topic.name)
    return topic

@router.put("/topics/{topic_id}/feeds", response_model=Topic)
async def update_topic_feeds_route(topic_id: str, feed_urls: List[str]):
    """Update the feed URLs for a topic."""
    try:
        topic = get_topic(topic_id)
        if not topic:
            error("TOPIC", "Not found", f"ID: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic.feed_urls = feed_urls
        save_topic(topic)
        return topic
    except Exception as e:
        error("TOPIC", "Feed update error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/topics/{topic_id}/update", response_model=dict)
async def schedule_topic_update_route(topic_id: str, background_tasks: BackgroundTasks):
    """Request a topic update (fetch feeds and process)."""
    try:
        topic = get_topic(topic_id)
        if not topic:
            error("TOPIC", "Not found", f"ID: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic not found")
        
        background_tasks.add_task(request_topic_update, topic_id)
        debug("TOPIC", "Update scheduled", topic.name)
        return {"message": f"Update scheduled for topic {topic_id}"}
    except Exception as e:
        error("TOPIC", "Update scheduling error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/topics/{topic_id}", response_model=dict)
async def delete_topic_route(topic_id: str):
    """Delete a specific topic."""
    try:
        topic = get_topic(topic_id)
        if not topic:
            error("TOPIC", "Not found", f"ID: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic not found")
        
        mark_topic_deleted(topic_id)
        info("TOPIC", "Deleted", topic.name)
        return {"message": f"Topic {topic_id} deleted"}
    except Exception as e:
        error("TOPIC", "Deletion error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/topics/{topic_id}", response_model=Topic)
async def update_topic_route(topic_id: str, topic_update: TopicUpdate):
    """Update a topic's details."""
    try:
        # Get existing topic
        topic = get_topic(topic_id)
        if not topic:
            error("TOPIC", "Not found", f"ID: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Update only non-null values
        update_data = topic_update.model_dump(exclude_unset=True)
        
        # Special handling for thumbnail_url
        if "thumbnail_url" in update_data:
            thumbnail_url = update_data["thumbnail_url"]
            if not thumbnail_url or thumbnail_url.lower() in ["auto", "none", ""]:
                # Generate new thumbnail
                thumbnail_data = get_random_thumbnail(f"{topic.name} {topic.description}")
                update_data["thumbnail_url"] = thumbnail_data.get("thumbnail_url")
        
        # Update topic
        for key, value in update_data.items():
            setattr(topic, key, value)
        
        # Save updated topic
        updated_topic = update_topic(topic_id, update_data)
        info("TOPIC", "Updated", topic.name)
        return updated_topic
    except Exception as e:
        error("TOPIC", "Update error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/topics/{topic_id}/publish", response_model=dict)
async def publish_topic_route(topic_id: str, background_tasks: BackgroundTasks):
    """Publish a topic to its configured destinations."""
    try:
        topic = get_topic(topic_id)
        if not topic:
            error("TOPIC", "Not found", f"ID: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic not found")
        
        background_tasks.add_task(request_topic_publish, topic)
        debug("TOPIC", "Publishing scheduled", topic.name)
        return {"message": f"Publishing scheduled for topic {topic_id}"}
    except Exception as e:
        error("TOPIC", "Publishing error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
