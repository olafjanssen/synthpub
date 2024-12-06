"""
Database operations for topics using individual YAML files.
"""
from pathlib import Path
from typing import Dict, Optional, List
import yaml
import uuid
from datetime import datetime
from shutil import move
import os
from functools import wraps

from api.models import Topic
from api.models.feed_item import FeedItem

# In-memory cache for topics
_topic_cache: Dict[str, Topic] = {}
_cache_initialized = False

def _invalidate_cache():
    """Clear the topic cache."""
    global _topic_cache, _cache_initialized
    _topic_cache.clear()
    _cache_initialized = False

def _ensure_cache():
    """Initialize cache if not already done."""
    global _cache_initialized
    if not _cache_initialized:
        topics = _load_all_topics_from_disk()
        _topic_cache.update({topic.id: topic for topic in topics})
        _cache_initialized = True

def _load_all_topics_from_disk() -> List[Topic]:
    """Internal function to load topics directly from disk."""
    ensure_db_exists()
    topics = []
    for file in DB_PATH().glob("*.yaml"):
        if not file.name.startswith('_'):
            with open(file, "r", encoding="utf-8") as f:
                topics.append(Topic(**yaml.safe_load(f)))
    return topics

def DB_PATH():
    return Path(os.getenv("DB_PATH", "../db")) / 'topics'

def ensure_db_exists():
    """Create the topics directory if it doesn't exist."""
    DB_PATH().mkdir(parents=True, exist_ok=True)

def save_topic(topic: Topic) -> None:
    """Save topic to individual YAML file and update cache."""
    ensure_db_exists()
    
    filename = DB_PATH() / f"{topic.id}.yaml"
    topic_dict = topic.model_dump()
    
    if 'feed_items' in topic_dict:
        for item in topic_dict['feed_items']:
            if 'accessed_at' in item:
                item['accessed_at'] = item['accessed_at'].isoformat()
    
    with open(filename, "w", encoding="utf-8") as f:
        yaml.safe_dump(topic_dict, f, sort_keys=False, allow_unicode=True)
    
    # Update cache
    _topic_cache[topic.id] = topic

def get_topic(topic_id: str) -> Optional[Topic]:
    """Retrieve topic by id from cache or disk."""
    _ensure_cache()
    return _topic_cache.get(topic_id)

def list_topics() -> List[Topic]:
    """List all active (non-deleted) topics from cache."""
    _ensure_cache()
    return list(_topic_cache.values())

def load_topics() -> Dict[str, Topic]:
    """Load all topics into a dictionary from cache."""
    _ensure_cache()
    return dict(_topic_cache)

def create_topic(title: str, description: str) -> Topic:
    """Create a new topic and add to cache."""
    topic_id = str(uuid.uuid4())
    topic = Topic(id=topic_id, title=title, description=description)
    save_topic(topic)
    return topic

def mark_topic_deleted(topic_id: str) -> bool:
    """Mark a topic as deleted and remove from cache."""
    filename = DB_PATH() / f"{topic_id}.yaml"
    if not filename.exists():
        return False
    
    new_filename = DB_PATH() / f"_{topic_id}.yaml"
    move(filename, new_filename)
    
    # Remove from cache
    _topic_cache.pop(topic_id, None)
    return True

def update_topic(topic_id: str, updated_data: dict) -> Optional[Topic]:
    """Update a topic and refresh cache."""
    topic = get_topic(topic_id)
    if not topic:
        return None
    
    for key, value in updated_data.items():
        if hasattr(topic, key):
            setattr(topic, key, value)
    
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