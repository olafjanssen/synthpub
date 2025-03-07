"""
Example script demonstrating the logging system in SynthPub.

This script shows how to use both system-level and user-facing logs.
Run it to see how logs are recorded and filtered by level.
"""
import sys
import os
import time
import random

# Add the parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import logging utilities
from utils.logging import (
    debug, info, warning, error, critical, 
    user_info, user_warning, user_error,
    get_recent_logs, get_user_logs
)

def simulate_topic_creation():
    """Simulate creating a topic with logging."""
    debug("Starting topic creation process")
    
    # Simulate some work
    time.sleep(0.5)
    
    topic_name = f"Example Topic {random.randint(1, 100)}"
    info(f"Creating new topic: {topic_name}")
    
    # Successful creation - log to user
    user_info(f"Created new topic: {topic_name}")
    
    return topic_name

def simulate_feed_processing(topic_name):
    """Simulate processing feeds for a topic with logging."""
    debug(f"Starting feed processing for topic: {topic_name}")
    
    # Log processing start
    info(f"Processing feeds for topic: {topic_name}")
    user_info(f"Searching for content related to '{topic_name}'")
    
    # Simulate work
    time.sleep(1)
    
    # Simulate finding some feed items
    found_items = random.randint(0, 5)
    
    if found_items == 0:
        warning(f"No relevant feed items found for topic: {topic_name}")
        user_warning(f"No relevant content found for '{topic_name}'. Try adjusting the topic description.")
    else:
        info(f"Found {found_items} relevant feed items for topic: {topic_name}")
        user_info(f"Found {found_items} relevant articles for '{topic_name}'")
        
    return found_items

def simulate_article_generation(topic_name, feed_items):
    """Simulate article generation with logging."""
    debug(f"Starting article generation for topic: {topic_name} with {feed_items} feed items")
    
    # Log generation start
    info(f"Generating article for topic: {topic_name}")
    user_info(f"Generating article for '{topic_name}'")
    
    # Simulate work
    time.sleep(1.5)
    
    # Simulate success or failure based on feed items
    if feed_items > 0:
        info(f"Article generation successful for topic: {topic_name}")
        user_info(f"Article for '{topic_name}' generated successfully")
        return True
    else:
        error(f"Failed to generate article for topic: {topic_name} - insufficient content")
        user_error(f"Could not generate article for '{topic_name}' - insufficient content")
        return False

def simulate_publishing(topic_name, article_generated):
    """Simulate publishing an article with logging."""
    if not article_generated:
        debug(f"Skipping publishing for topic: {topic_name} - no article generated")
        return
    
    debug(f"Starting publishing process for topic: {topic_name}")
    
    # Log publish start
    info(f"Publishing article for topic: {topic_name}")
    user_info(f"Publishing article for '{topic_name}'")
    
    # Simulate work
    time.sleep(1)
    
    # Simulate random success/failure
    if random.random() > 0.2:  # 80% success rate
        info(f"Article published successfully for topic: {topic_name}")
        user_info(f"Article for '{topic_name}' published successfully")
    else:
        error(f"Failed to publish article for topic: {topic_name}")
        user_error(f"Failed to publish article for '{topic_name}'. Please try again.")

def simulate_workflow():
    """Simulate a complete content workflow with logging."""
    # Simulate creating a topic
    topic_name = simulate_topic_creation()
    
    # Simulate processing feeds
    feed_items = simulate_feed_processing(topic_name)
    
    # Simulate article generation
    article_generated = simulate_article_generation(topic_name, feed_items)
    
    # Simulate publishing
    simulate_publishing(topic_name, article_generated)
    
    # Display summary of logs
    print("\n=== Recent User-Facing Logs ===")
    for log in get_user_logs():
        print(f"{log['timestamp'][:19]} | {log['level']} | {log['message']}")
        
    print("\n=== All Recent Logs ===")
    for log in get_recent_logs():
        print(f"{log['timestamp'][:19]} | {log['level']} | {log['message']}")

if __name__ == "__main__":
    print("=== SynthPub Logging Example ===")
    print("This script demonstrates how the logging system works.")
    print("Notice how some logs are marked as user-facing while others are system-only.")
    print()
    
    simulate_workflow() 