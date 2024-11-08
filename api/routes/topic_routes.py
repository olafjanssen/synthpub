"""Topic-related API routes."""
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from ..models.topic import Topic, TopicCreate
from ..db.topic_db import load_topics, save_topics
from ..db.article_db import create_article
from curator.article_generator import generate_article

router = APIRouter()

@router.post("/topics/", response_model=Topic)
async def create_topic_route(topic: TopicCreate):
    """Create a new topic and generate its initial article."""
    try:
        topics = load_topics()
        
        # Generate topic ID first
        topic_id = str(uuid4())
        
        # Generate article content
        title, content = generate_article(topic.description)
        
        # Save article with topic ID
        article_id = create_article(
            title=title,
            topic_id=topic_id,
            content=content
        ).id
        
        # Create new topic
        topic_data = Topic(
            id=topic_id,
            name=topic.name,
            description=topic.description,
            article=article_id
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