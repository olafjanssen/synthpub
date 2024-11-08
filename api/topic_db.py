"""
Database operations for topics using JSON file storage.
"""
import json
from pathlib import Path
from typing import Dict
from api.models import Topic

DB_PATH = Path("db/topics.json")

def init_db():
    """Initialize the database file if it doesn't exist."""
    DB_PATH.parent.mkdir(exist_ok=True)
    if not DB_PATH.exists():
        DB_PATH.write_text("{}")

def load_topics() -> Dict[str, Topic]:
    """Load topics from JSON file."""
    init_db()
    content = DB_PATH.read_text()
    data = json.loads(content)
    # Convert directly to Topic objects
    topics = {id_str: Topic(**topic_data) for id_str, topic_data in data.items()}
    return topics

def save_topics(topics: Dict[str, Topic]):
    """Save topics to JSON file."""
    init_db()
    # Direct conversion to dict
    data = {id_: topic.model_dump() for id_, topic in topics.items()}
    DB_PATH.write_text(json.dumps(data, indent=2))