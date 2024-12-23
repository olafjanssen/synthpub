"""Scheduler for automatically updating topics."""
import time
from datetime import datetime, timedelta
import logging
from typing import List
from api.db.topic_db import list_topics
from api.models.topic import Topic
import os
from dotenv import load_dotenv
from api.signals import topic_update_requested

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
UPDATE_INTERVAL_MINUTES = int(os.getenv('TOPIC_UPDATE_INTERVAL_MINUTES', 1))
TOPIC_UPDATE_THRESHOLD_HOURS = int(os.getenv('TOPIC_UPDATE_THRESHOLD_HOURS', 1))

# Dictionary to store last check times for topics
_last_checked_times = {}

def should_update_topic(topic: Topic) -> bool:
    """Check if a topic should be updated based on its last check time."""
    if topic.id not in _last_checked_times:
        return True
        
    time_since_check = datetime.now() - _last_checked_times[topic.id]
    return time_since_check > timedelta(hours=TOPIC_UPDATE_THRESHOLD_HOURS)

def check_and_update_topics():
    """Check all topics and trigger updates if needed."""
    try:
        topics = list_topics()
        if not topics:
            logger.info("No topics found to update")
            return

        for topic in topics:
            if should_update_topic(topic):
                logger.info(f"Updating topic {topic.id}")
                topic_update_requested.send('news_scheduler', topic_id=topic.id)
            
    except Exception as e:
        logger.error(f"Error in check_and_update_topics: {str(e)}")

def run_scheduler():
    """Run the scheduler loop."""
    logger.info("Starting topic update scheduler")
    
    while True:
        try:
            check_and_update_topics()
            time.sleep(UPDATE_INTERVAL_MINUTES * 60)  # Convert minutes to seconds
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying after error

def start_scheduler():
    """Start the scheduler."""
    try:
        run_scheduler()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler stopped due to error: {str(e)}")

if __name__ == "__main__":
    start_scheduler()