"""Topic-related API routes."""
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from ..models.topic import Topic, TopicCreate
from ..db.topic_db import load_topics, save_topics
from ..db.article_db import create_article, get_article, update_article
from curator.topic_manager import create_new_topic, process_topic_updates
from typing import List

router = APIRouter()

@router.post("/topics/", response_model=Topic)
async def create_topic_route(topic: TopicCreate):
    """Create a new topic and generate its initial article."""
    try:
        topics = load_topics()
        topic_id = str(uuid4())
        
        # Create topic and initial article
        article_id, topic_data = create_new_topic(
            topic=topic,
            create_article_fn=create_article,
            topic_id=topic_id
        )
        
        # Save to database
        topics[topic_data.id] = topic_data
        save_topics(topics)
        
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
    
    topic = topics[topic_id]
    topic.feed_urls = feed_urls
    save_topics(topics)
    
    return topic

@router.post("/topics/{topic_id}/update", response_model=Topic)
async def update_topic_route(topic_id: str):
    """Update topic article based on feed content."""
    try:
        # Load data
        topics = load_topics()
        if topic_id not in topics:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic = topics[topic_id]
        current_article = get_article(topic.article)
        if not current_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Process updates
        updated_article, new_feed_items = process_topic_updates(
            topic=topic,
            current_article=current_article,
            update_article_fn=update_article
        )
        
        if updated_article:
            # Update topic with new data
            topic.article = updated_article.id
            topic.processed_feeds.extend(new_feed_items)
            save_topics(topics)
        
        return topic
        
    except Exception as e:
        print(f"Error updating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")