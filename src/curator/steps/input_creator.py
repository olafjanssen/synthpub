"""
Input creator step for the curator workflow.

This module handles loading topic and article data based on the topic_id.
"""
from typing import Dict, Any, Optional

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from utils.logging import warning, debug, error
from api.db.article_db import get_article
from api.db.topic_db import get_topic

def process(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create input by loading topic and article data from the database.
    
    Args:
        state: Current workflow state with at least topic_id
        
    Returns:
        Updated state with topic and existing_article
    """
    debug("CURATOR", "Preparing curator inputs")
    
    # Create new state starting with current state
    new_state = {**state, "current_step": "input_creator"}
    
    # Extract the topic_id (this is the only required input)
    topic_id = state.get("topic_id")
    if not topic_id:
        new_state["has_error"] = True
        new_state["error_message"] = "No topic_id provided"
        new_state["error_step"] = "input_creator"
        return new_state
        
    try:
        # Load the topic from the database
        topic = get_topic(topic_id)
        if not topic:
            new_state["has_error"] = True
            new_state["error_message"] = f"Topic not found: {topic_id}"
            new_state["error_step"] = "input_creator"
            return new_state
        
        # Check if the feed item has been processed before
        feed_item = state.get("feed_item")
        if feed_item and is_already_processed(topic, feed_item):
            debug("CURATOR", "Feed already processed", f"URL: {feed_item.url}")
            new_state["has_error"] = True
            new_state["error_message"] = f"Feed item already processed: {feed_item.url}"
            new_state["error_step"] = "input_creator"
            return new_state
        
        # Get the current article if one exists
        article = None
        if topic.article:
            article = get_article(topic.article)
            if not article:
                warning("CURATOR", "Referenced article not found", f"Topic: {topic.name}, Article ID: {topic.article}")
                # Don't treat missing article as error - we'll generate a new one
                debug("CURATOR", "Will generate new article", f"Topic: {topic.name}")
        
        # Update the state with loaded data
        new_state["topic"] = topic
        new_state["existing_article"] = article
        
        return new_state
        
    except Exception as e:
        error_message = str(e)
        error("CURATOR", "Input creation failed", error_message)
        new_state["has_error"] = True
        new_state["error_message"] = f"Failed to load topic data: {error_message}"
        new_state["error_step"] = "input_creator"
        return new_state

def is_already_processed(topic: Topic, feed_item: FeedItem) -> bool:
    """Check if a feed item has already been processed for this topic."""
    # Create a lookup dictionary of processed items by URL and content hash
    processed_items = {
        (item.url, item.content_hash): item 
        for item in topic.processed_feeds
    }
    
    # Check if this item is in the processed items
    return (feed_item.url, feed_item.content_hash) in processed_items             
