"""
Database operations for topics using individual YAML files.
"""
from pathlib import Path
from typing import Dict, Optional, List
import yaml
import uuid
from api.models import Topic
from datetime import datetime

from api.models.feed_item import FeedItem

DB_PATH = Path("db/topics")

def ensure_db_exists():
    """Create the topics directory if it doesn't exist."""
    DB_PATH.mkdir(parents=True, exist_ok=True)

def save_topic(topic: Topic) -> None:
    """Save topic to individual YAML file."""
    ensure_db_exists()
    
    # Generate filename from id
    filename = DB_PATH / f"{topic.id}.yaml"
    # Convert to dict and save
    topic_dict = topic.model_dump()
    # Convert datetime objects to ISO format
    if 'feed_items' in topic_dict:
        for item in topic_dict['feed_items']:
            if 'accessed_at' in item:
                item['accessed_at'] = item['accessed_at'].isoformat()
    
    with open(filename, "w", encoding="utf-8") as f:
        yaml.safe_dump(topic_dict, f, sort_keys=False, allow_unicode=True)

def get_topic(topic_id: str) -> Optional[Topic]:
    """Retrieve topic by id."""
    filename = DB_PATH / f"{topic_id}.yaml"
    
    if not filename.exists():
        return None
        
    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return Topic(**data)

def list_topics() -> List[Topic]:
    """List all topics."""
    ensure_db_exists()
    
    topics = []
    for file in DB_PATH.glob("*.yaml"):
        with open(file, "r", encoding="utf-8") as f:
            topics.append(Topic(**yaml.safe_load(f)))
            
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

def load_feed_items(items_data: List[dict]) -> List[FeedItem]:
    """Convert feed item dictionaries to FeedItem objects."""
    feed_items = []
    for item in items_data:
        try:
            item['accessed_at'] = datetime.fromisoformat(item['accessed_at'])
            feed_items.append(FeedItem(**item))
        except Exception as e:
            print(f"Error parsing feed item: {e}")
    return feed_items