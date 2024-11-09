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
    # Load topic
    topics = load_topics()
    if topic_id not in topics:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic = topics[topic_id]
    
    try:
        # Get current article
        current_article = get_article(topic.article)
        if not current_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Process all feeds
        feed_contents = process_feeds(topic.feed_urls)
        
        # Start with the current article content
        refined_content = current_article.content
        latest_article = current_article
        
        # Refine the article iteratively with each feed entry
        for feed_entry in feed_contents:
            # Create context for this feed entry
            entry_context = f"From {feed_entry['url']}:\n{feed_entry['title']}\n{feed_entry['content'][:500]}..."
            
            # Refine the article with this entry's content
            refined_content = refine_article(refined_content, entry_context)
            
            # Create new version of the article with same title
            latest_article = update_article(
                article_id=latest_article.id,
                content=refined_content
            )
            
            # Update topic reference
            topic.article = latest_article.id
        
        # Save final topic state
        save_topics(topics)
        return topic
        
    except Exception as e:
        print(f"Error updating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")