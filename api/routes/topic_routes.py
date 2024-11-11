"""Topic-related API routes."""
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from ..models.topic import Topic, TopicCreate
from ..db.topic_db import load_topics, save_topics
from ..db.article_db import create_article, get_article, update_article
from curator.article_generator import generate_article
from curator.feeds.feed_processor import process_feeds
from curator.article_refiner import refine_article
from typing import List

router = APIRouter()

@router.post("/topics/", response_model=Topic)
async def create_topic_route(topic: TopicCreate):
    """Create a new topic and generate its initial article."""
    try:
        topics = load_topics()
        
        # Generate topic ID first
        topic_id = str(uuid4())
        
        # Generate article content using topic description
        content = generate_article(topic.description)
        
        # Save article with topic ID and topic name as title
        article_id = create_article(
            title=topic.name,
            topic_id=topic_id,
            content=content
        ).id
        
        # Create new topic with feed URLs
        topic_data = Topic(
            id=topic_id,
            name=topic.name,
            description=topic.description,
            article=article_id,
            feed_urls=topic.feed_urls  # Include feed URLs from request
        )
        
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
        # Load topic
        topics = load_topics()
        if topic_id not in topics:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic = topics[topic_id]
        
        # Process feeds and get feed items
        feed_contents, feed_items = process_feeds(topic.feed_urls)
        
        # Filter out already processed feeds
        processed_urls = {item.url for item in topic.processed_feeds}
        new_feed_items = [
            item for item in feed_items 
            if item.url not in processed_urls
        ]
        
        if not new_feed_items:
            return topic
            
        # Update article with new content
        current_article = get_article(topic.article)
        if not current_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Refine article with new content
        refined_content = current_article.content
        for content, feed_item in zip(feed_contents, new_feed_items):
            refined_content = refine_article(refined_content, content)
            # Create new version for each feed item
            current_article = update_article(
                article_id=current_article.id,
                content=refined_content,
                feed_item=feed_item
            )
            if not current_article:
                raise HTTPException(status_code=500, detail="Failed to update article")
        
        # Update topic with new article and feed items
        topic.article = current_article.id
        topic.processed_feeds.extend(new_feed_items)
        
        # Save updated topic
        save_topics(topics)
        return topic
        
    except Exception as e:
        print(f"Error updating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")