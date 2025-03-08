"""Scheduler for automatically updating topics."""
import time
import threading
import yaml
from datetime import datetime, timedelta
from api.db.topic_db import list_topics
from api.models.topic import Topic
import os
from api.signals import topic_update_requested
from utils.logging import info, error

# Default configuration values
DEFAULT_UPDATE_INTERVAL_MINUTES = 15
DEFAULT_TOPIC_UPDATE_THRESHOLD_HOURS = 1
DEFAULT_SCHEDULER_ENABLED = True

# Dictionary to store last check times for topics
_last_checked_times = {}
_scheduler_thread = None
_should_stop = False

def load_settings():
    """Load scheduler settings from settings.yaml."""
    try:
        if os.path.exists("settings.yaml"):
            with open("settings.yaml", 'r') as f:
                settings = yaml.safe_load(f) or {}
                scheduler_settings = settings.get("scheduler", {})
                
                update_interval = scheduler_settings.get("update_interval_minutes", DEFAULT_UPDATE_INTERVAL_MINUTES)
                threshold_hours = scheduler_settings.get("update_threshold_hours", DEFAULT_TOPIC_UPDATE_THRESHOLD_HOURS)
                enabled = scheduler_settings.get("enabled", DEFAULT_SCHEDULER_ENABLED)
                
                return update_interval, threshold_hours, enabled
    except Exception as e:
        error("SCHEDULER", "Error loading settings", str(e))
    
    # Return defaults if anything fails
    return DEFAULT_UPDATE_INTERVAL_MINUTES, DEFAULT_TOPIC_UPDATE_THRESHOLD_HOURS, DEFAULT_SCHEDULER_ENABLED

def should_update_topic(topic: Topic) -> bool:
    """Check if a topic should be updated based on its last check time."""
    if topic.id not in _last_checked_times:
        return True
    
    _, threshold_hours, _ = load_settings()    
    time_since_check = datetime.now() - _last_checked_times[topic.id]
    return time_since_check > timedelta(hours=threshold_hours)

def check_and_update_topics():
    """Check all topics and trigger updates if needed."""
    try:
        topics = list_topics()
        if not topics:
            info("SCHEDULER", "No topics found to update")
            return

        for topic in topics:
            if should_update_topic(topic):
                info("SCHEDULER", "Signaling topic update", topic.id)
                topic_update_requested.send('news_scheduler', topic_id=topic.id)
                _last_checked_times[topic.id] = datetime.now()
            
    except Exception as e:
        error("SCHEDULER", "Error in check_and_update_topics", str(e))

def run_scheduler():
    """Run the scheduler loop."""
    global _should_stop
    
    info("SCHEDULER", "Starting")
    
    while not _should_stop:
        try:
            update_interval, _, enabled = load_settings()
            
            if enabled:
                check_and_update_topics()
            else:
                info("SCHEDULER", "Scheduler is disabled in settings")
            
            # Sleep for the configured interval
            time.sleep(update_interval * 60)  # Convert minutes to seconds
        except Exception as e:
            error("SCHEDULER", "Error in scheduler loop", str(e))
            time.sleep(60)  # Wait a minute before retrying after error

def start_scheduler_thread():
    """Start the scheduler in a background thread."""
    global _scheduler_thread, _should_stop
    
    if _scheduler_thread and _scheduler_thread.is_alive():
        info("SCHEDULER", "Scheduler already running")
        return
    
    _should_stop = False
    _scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    _scheduler_thread.start()
    info("SCHEDULER", "Scheduler started in background thread")

def stop_scheduler_thread():
    """Stop the scheduler thread."""
    global _should_stop
    
    _should_stop = True
    info("SCHEDULER", "Scheduler stopping")

if __name__ == "__main__":
    # Direct execution for testing
    try:
        run_scheduler()
    except KeyboardInterrupt:
        info("SCHEDULER", "Stopped by user")
    except Exception as e:
        error("SCHEDULER", "Stopped due to error", str(e))