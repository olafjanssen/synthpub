"""Scheduler for automatically updating topics."""

import threading
import yaml
from datetime import datetime, timedelta
from api.db.topic_db import list_topics
from api.models.topic import Topic
import os
from utils.logging import info, error
from curator.topic_updater import queue_topic_update

# Default configuration values
DEFAULT_UPDATE_INTERVAL_MINUTES = 15
DEFAULT_TOPIC_UPDATE_THRESHOLD_HOURS = 1
DEFAULT_SCHEDULER_ENABLED = True

# Dictionary to store last check times for topics
_last_checked_times = {}
_scheduler_thread = None
_stop_event = threading.Event()

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
                queue_topic_update(topic.id, sender='news_scheduler')
                _last_checked_times[topic.id] = datetime.now()
            
    except Exception as e:
        error("SCHEDULER", "Error in check_and_update_topics", str(e))

def run_scheduler():
    """Run the scheduler loop."""
    info("SCHEDULER", "Starting scheduler monitoring loop")
    
    while not _stop_event.is_set():
        try:
            # Load settings on every iteration to get the latest values
            update_interval, threshold_hours, enabled = load_settings()
            
            if enabled:
                info("SCHEDULER", f"Running update check (interval: {update_interval}m, threshold: {threshold_hours}h)")
                check_and_update_topics()
            else:
                info("SCHEDULER", "Scheduler is disabled in settings, skipping update check")
            
            # Wait for the specified interval or until stopped
            # Using wait with a short timeout allows responding to stop requests quickly
            wait_minutes = max(1, update_interval)
            seconds_to_wait = wait_minutes * 60
            
            # Wait in small increments to be responsive to stop requests
            wait_increment = 5  # Check every 5 seconds if we should stop
            for _ in range(0, seconds_to_wait, wait_increment):
                if _stop_event.wait(wait_increment):
                    # Stop event was set, exit the loop
                    info("SCHEDULER", "Stop requested during wait period")
                    return
                
        except Exception as e:
            error("SCHEDULER", "Error in scheduler loop", str(e))
            # Short wait for error recovery
            _stop_event.wait(10)  # Wait 10 seconds before retrying after error

def start_scheduler_thread():
    """Start the scheduler in a background thread."""
    global _scheduler_thread
    
    # Reset the stop event
    _stop_event.clear()
    
    # Check if the scheduler is enabled in settings
    _, _, enabled = load_settings()
    
    # If scheduler is already running, check if it should continue
    if _scheduler_thread and _scheduler_thread.is_alive():
        info("SCHEDULER", "Scheduler thread already running")
        return
    
    # Start the thread (it will check enabled setting internally)
    _scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    _scheduler_thread.start()
    
    if enabled:
        info("SCHEDULER", "Scheduler started and enabled in background thread")
    else:
        info("SCHEDULER", "Scheduler thread started but waiting (disabled in settings)")

def stop_scheduler_thread():
    """Stop the scheduler thread."""
    global _scheduler_thread
    
    # Signal the thread to stop
    info("SCHEDULER", "Signaling scheduler to stop")
    _stop_event.set()
    
    # Wait for the thread to finish if it's running
    if _scheduler_thread and _scheduler_thread.is_alive():
        # Set a timeout to prevent hanging indefinitely
        _scheduler_thread.join(timeout=3.0)
        if _scheduler_thread.is_alive():
            error("SCHEDULER", "Failed to stop scheduler thread within timeout")
        else:
            info("SCHEDULER", "Scheduler thread stopped cleanly")
            _scheduler_thread = None
    else:
        info("SCHEDULER", "No scheduler thread running")

if __name__ == "__main__":
    # Direct execution for testing
    try:
        run_scheduler()
    except KeyboardInterrupt:
        info("SCHEDULER", "Stopped by user")
    except Exception as e:
        error("SCHEDULER", "Stopped due to error", str(e))