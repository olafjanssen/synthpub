"""Topic-related API routes."""
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from api.models.topic import Topic, TopicCreate, TopicUpdate
from api.db.topic_db import load_topics, mark_topic_deleted, update_topic, get_topic, save_topic
from api.db.article_db import create_article
from curator.article_generator import generate_article
from typing import List
from api.signals import topic_update_requested
from curator.topic_updater import handle_topic_publishing
from services.pexels_service import get_random_thumbnail

router = APIRouter()

@router.post("/topics/", response_model=Topic)
async def create_topic_route(topic: TopicCreate):
    """Create a new topic and generate its initial article."""
    try:
        topic_id = str(uuid4())
        
        # Check if we should generate a thumbnail
        thumbnail_url = topic.thumbnail_url
        
        # Generate a thumbnail if:
        # 1. Field is None (not provided in request)
        # 2. Field is an empty string (user left the field blank)
        # 3. Field is "auto" or "none" (explicit request for auto-generation)
        should_generate = (
            thumbnail_url is None or 
            (isinstance(thumbnail_url, str) and (
                thumbnail_url.strip() == "" or
                thumbnail_url.lower().strip() in ["auto", "none"]
            ))
        )
        
        if should_generate:
            search_text = f"{topic.name} {topic.description}"
            thumbnail_data = get_random_thumbnail(search_text)
            thumbnail_url = thumbnail_data.get("thumbnail_url")
        
        # At this point thumbnail_url is either:
        # - A URL from Pexels (if auto-generated)
        # - A custom URL provided by the user (if not auto-generated)
        # - None if thumbnail generation failed
        
        # Create topic and initial article
        content = generate_article(topic.name, topic.description)
            
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
            feed_urls=topic.feed_urls,
            thumbnail_url=thumbnail_url
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
        
        # Get the topic data for potential thumbnail generation
        topic_data = topic_update.model_dump(exclude_unset=True)
        
        # Special handling for thumbnail_url
        if hasattr(topic_update, 'thumbnail_url') and topic_update.thumbnail_url is not None:
            thumbnail_url = topic_update.thumbnail_url.strip()
            
            # Check if we should generate a new thumbnail
            if thumbnail_url == "" or thumbnail_url.lower() in ["auto", "none"]:
                # Get data for search terms
                name = topic_update.name
                description = topic_update.description
                
                # If name and description aren't being updated, get them from the existing topic
                if not name or not description:
                    existing_topic = get_topic(topic_id)
                    if existing_topic:
                        name = name or existing_topic.name
                        description = description or existing_topic.description
                
                search_text = f"{name} {description}"
                thumbnail_data = get_random_thumbnail(search_text)
                topic_data['thumbnail_url'] = thumbnail_data.get("thumbnail_url")
            else:
                # Use the provided URL
                topic_data['thumbnail_url'] = thumbnail_url
        
        # Update the topic
        updated_topic = update_topic(topic_id, topic_data)
            
        if not updated_topic:
            raise HTTPException(status_code=500, detail="Failed to update topic")
        
        return updated_topic
        
    except Exception as e:
        print(f"Error updating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/topics/{topic_id}/publish", response_model=dict)
async def publish_topic_route(topic_id: str):
    """Request topic publish via signal."""
    try:
        # Check if topic exists
        topics = load_topics()
        if topic_id not in topics:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Publish topic
        topic = get_topic(topic_id)
        handle_topic_publishing(topic)

        return {"message": "Topic published", "topic_id": topic_id}
        
    except Exception as e:
        print(f"Error publishing topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
