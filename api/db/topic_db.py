"""
Database operations for topics using individual JSON files.
"""
from pathlib import Path
from typing import Dict, Optional, List
import json
import uuid
from api.models import Topic

DB_PATH = Path("db/topics")

def ensure_db_exists():
    """Create the topics directory if it doesn't exist."""
    DB_PATH.mkdir(parents=True, exist_ok=True)

def save_topic(topic: Topic) -> None:
    """Save topic to individual JSON file."""
    ensure_db_exists()
    
    # Generate filename from id
    filename = DB_PATH / f"{topic.id}.json"
    
    # Convert to dict and save
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(topic.model_dump(), f, indent=2)

def get_topic(topic_id: str) -> Optional[Topic]:
    """Retrieve topic by id."""
    filename = DB_PATH / f"{topic_id}.json"
    
    if not filename.exists():
        return None
        
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        return Topic(**data)

def list_topics() -> List[Topic]:
    """List all topics."""
    ensure_db_exists()
    
    topics = []
    for file in DB_PATH.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            topics.append(Topic(**json.load(f)))
            
    return topics

def load_topics() -> Dict[str, Topic]:
    """Load all topics into a dictionary."""
    topics = list_topics()
    return {topic.id: topic for topic in topics}

def save_topics(topics: Dict[str, Topic]):
    """Save multiple topics."""
    ensure_db_exists()
    for topic in topics.values():
        save_topic(topic)

def create_topic(title: str, description: str) -> Topic:
    """Create an new topic."""
    topic_id = str(uuid.uuid4())
    topic = Topic(id=topic_id, title=title, description=description)
    save_topic(topic)
    return topic