"""
FastAPI application for the Curator API.
"""
from fastapi import FastAPI, HTTPException
from .models import TopicCreate, Topic
from curator.article_generator import generate_article
from api.db import load_topics, save_topics

app = FastAPI(title="SynthPub API")

@app.post("/topics/", response_model=Topic)
async def create_topic(topic: TopicCreate):
    """Create a new topic and generate its initial article."""
    
    # Load existing topics
    topics = load_topics()
    
    # Check if topic already exists
    if topic.name in topics:
        raise HTTPException(status_code=400, detail="Topic already exists")
    
    # Generate article from topic description
    article = generate_article(topic.description)
    
    # Create new topic
    topic_data = Topic(
        name=topic.name,
        description=topic.description,
        article=article
    )
    
    # Store topic and save to file
    topics[topic.name] = topic_data
    save_topics(topics)
    
    return topic_data

@app.get("/topics/", response_model=list[Topic])
async def list_topics():
    """List all topics."""
    topics = load_topics()
    return list(topics.values())