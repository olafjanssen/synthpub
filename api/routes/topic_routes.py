"""Topic-related API routes."""
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from api.models.topic import Topic, TopicCreate, TopicUpdate
from api.models.feed_item import FeedItem
from api.models.article import Article
from api.db.topic_db import load_topics, save_topics, mark_topic_deleted, update_topic, get_topic, save_topic
from api.db.article_db import create_article, get_article, update_article
from curator.article_generator import generate_article
from curator.article_refiner import refine_article
from curator.article_relevance_filter import filter_relevance
from typing import List, Tuple, Optional
from curator.feeds.feed_processor import process_feeds

router = APIRouter()

def process_feed_item(
    topic: Topic,
    current_article: Article,
    feed_content: str,
    feed_item: FeedItem
) -> Optional[Article]:
    """Process a single feed item for a topic."""
    # Skip if content not relevant
    if not filter_relevance(topic.description, current_article.content, feed_content):
        return None
        
    # Update article with new content
    refined_content = refine_article(current_article.content, feed_content)
    updated_article = update_article(
        article_id=current_article.id,
        content=refined_content,
        feed_item=feed_item
    )
    
    return updated_article

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
    
    topic = topics[topic_id]
    topic.feed_urls = feed_urls
    save_topics(topics)
    
    return topic

@router.post("/topics/{topic_id}/update", response_model=Topic)
async def update_topic_route(topic_id: str):
    """Update topic article based on feed content."""
    try:
        # Load topic
        topic = get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        current_article = get_article(topic.article)
        if not current_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Process feeds
        feed_contents, feed_items = process_feeds(topic.feed_urls)
        processed_items = {(item.url, item.content_hash): item for item in topic.processed_feeds}
        
        # Process each feed item
        for content, feed_item in zip(feed_contents, feed_items):
            # Skip if already processed
            if (feed_item.url, feed_item.content_hash) in processed_items:
                continue
            
            # Process single feed item
            updated_article = process_feed_item(
                topic=topic,
                current_article=current_article,
                feed_content=content,
                feed_item=feed_item,
            )
            
            # Mark relevance and add to processed feeds
            feed_item.is_relevant = updated_article is not None
            topic.processed_feeds.append(feed_item)
            
            # Update current article if content was relevant
            if updated_article:
                current_article = updated_article
                topic.article = updated_article.id
        
            # Save updated topic
            save_topic(topic)
        return topic
        
    except Exception as e:
        print(f"Error updating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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