from fastapi import HTTPException
from api.models.topic import Topic
from api.models.article import Article
from api.db.topic_db import get_topic, save_topic
from api.db.article_db import get_article, update_article, create_article
from curator.article_relevance_filter import filter_relevance
from curator.article_refiner import refine_article
from curator.article_generator import generate_article
from api.models.feed_item import FeedItem
from typing import Optional
from api.signals import topic_update_requested, topic_updated, news_feed_update_requested, news_feed_item_found, publish_requested, article_updated, convert_requested, article_generation_requested
from utils.logging import debug, info, warning, error, user_info, user_warning, user_error
import threading
from queue import Queue
import news.feeds
import news.publishers
import news.converter   
import time

# Add queue for handling updates
update_queue = Queue()
feed_item_queue = Queue()  # New queue for feed items

def handle_topic_update(sender, topic_id):
    """Signal handler for topic update requests."""
    update_queue.put(topic_id)
    debug(f"Queued update request for topic {topic_id} from {sender}")  # Changed from print to debug
    user_info(f"Update queued for topic: {topic_id}")  # Added user-facing log

def handle_topic_publishing(sender):
    """Signal handler for topic publishing requests."""
    info(f"Publishing topic {sender.id}")  # Changed from print to info
    user_info(f"Publishing topic: {sender.name}")  # Added user-facing log
    
    # Process feeds
    topic = sender
    for publish_url in topic.publish_urls:
        # split publish_url into piped elements
        commands = [cmd.strip() for cmd in publish_url.split('|')]

        debug("Default conversion: content")  # Changed from print to debug
        convert_requested.send(topic, type="content")

        for cmd in commands:
            if cmd.startswith('convert://'):
                info(f"Converting to {cmd}")  # Changed from print to info
                convert_requested.send(topic, type=cmd.split('://', 1)[1].strip())
            else:
                info(f"Publishing to {cmd}")  # Changed from print to info
                publish_requested.send(topic, publish_url=cmd)

def handle_article_generation(sender, topic_id: str, topic_name: str, topic_description: str):
    """Signal handler for article generation requests."""
    try:
        info(f"Generating article for topic {topic_id}")  # Changed from print to info
        user_info(f"Starting article generation for topic: {topic_name}")  # Added user-facing log
        
        # Generate article content
        content = generate_article(topic_name, topic_description)
        
        # Create article in the database
        article = create_article(
            title=topic_name,
            topic_id=topic_id,
            content=content
        )
        
        # Update the topic with the new article ID
        topic = get_topic(topic_id)
        if topic:
            topic.article = article.id
            save_topic(topic)
            info(f"Article generated and saved for topic {topic_id}")  # Changed from print to info
            user_info(f"Article generated successfully for topic: {topic_name}")  # Added user-facing log
        else:
            warning(f"Error: Topic {topic_id} not found when updating with new article")  # Changed from print to warning
            user_warning(f"Topic not found when updating with new article: {topic_name}")  # Added user-facing log
            
    except Exception as e:
        error(f"Error generating article: {str(e)}")  # Changed from print to error
        user_error(f"Failed to generate article for topic '{topic_name}'")  # Added user-facing log

def process_update_queue():
    """Process queued topic updates and feed items."""
    while True:
        try:
            # Check for pending topic updates
            if not update_queue.empty():
                topic_id = update_queue.get()
                info(f"Processing update for topic {topic_id}")  # Changed from print to info
                try:
                    update_topic(topic_id)
                    user_info(f"Topic '{topic_id}' updated successfully")  # Added user-facing log
                except Exception as e:
                    error(f"Error updating topic {topic_id}: {str(e)}")  # Added error log
                    user_error(f"Update failed for topic '{topic_id}'")  # Added user-facing log
            
            # Check for pending feed items
            if not feed_item_queue.empty():
                feed_item_data = feed_item_queue.get()
                process_queued_feed_item(feed_item_data)
            
            # Small sleep to prevent CPU spinning
            if update_queue.empty() and feed_item_queue.empty():
                time.sleep(0.1)
                
        except Exception as e:
            error(f"Error processing queue item: {str(e)}")  # Changed from print to error

def process_queued_feed_item(feed_item_data):
    """Process a feed item from the queue."""
    try:
        debug(f"Processing feed item: {feed_item_data['feed_item'].url}")  # Changed from print to debug
        handle_feed_item(
            sender=feed_item_data['sender'],
            feed_url=feed_item_data['feed_url'],
            feed_item=feed_item_data['feed_item'],
            content=feed_item_data['content']
        )
    except Exception as e:
        error(f"Error processing feed item: {str(e)}")  # Changed from print to error

def handle_feed_item(sender, feed_url: str, feed_item: FeedItem, content: str):
    """Signal handler for feed item found."""
    info(f"Feed item found for {feed_url}: {feed_item.url}")  # Changed from print to info

    # If this item needs further processing, send a new feed update request
    if feed_item.needs_further_processing:
        debug(f"Item needs further processing: {feed_item.url}")  # Changed from print to debug
        news_feed_update_requested.send(sender, feed_url=feed_item.url)
        return

    topic = sender
    processed_items = {(item.url, item.content_hash): item for item in topic.processed_feeds}

    # Skip if already processed
    if (feed_item.url, feed_item.content_hash) in processed_items:
        debug(f"Skipping feed item {feed_item.url} as it has already been processed")  # Changed from print to debug
        return

    current_article = get_article(topic.article)
    if not current_article:
        error("Article not found")  # Added error log
        raise HTTPException(status_code=404, detail="Article not found")

    # Process single feed item
    updated_article = process_feed_item(
        topic=topic,
        current_article=current_article,
        feed_content=content,
        feed_item=feed_item,
    )
    
    # Mark relevance and add to processed feeds
    feed_item.is_relevant = updated_article is not None
    topic.processed_feeds.append(feed_item)
    
    # Update current article if content was relevant
    if updated_article:
        topic.article = updated_article.id
        user_info(f"New content added to topic '{topic.name}' from feed")  # Added user-facing log

    # Save updated topic
    topic_updated.send(topic)

    # Publish updated article
    if updated_article:
        article_updated.send(topic)

def queue_feed_item(sender, feed_url: str, feed_item: FeedItem, content: str):
    """Queue a feed item for processing."""
    debug(f"Queuing feed item: {feed_item.url}")  # Changed from print to debug
    feed_item_queue.put({
        'sender': sender,
        'feed_url': feed_url,
        'feed_item': feed_item,
        'content': content
    })

def start_update_processor():
    """Start the update processor thread."""
    # Connect signal handlers
    topic_update_requested.connect(handle_topic_update)
    news_feed_item_found.connect(queue_feed_item)
    article_updated.connect(handle_topic_publishing)
    article_generation_requested.connect(handle_article_generation)
    
    # Start queue processor thread
    processor_thread = threading.Thread(target=process_update_queue, daemon=True)
    processor_thread.start()
    info("Topic update processor started")  # Changed from print to info
    user_info("Content processing system started and ready")  # Added user-facing log
    
    return processor_thread  # Added return value for the thread

def process_feed_item(
    topic: Topic,
    current_article: Article,
    feed_content: str,
    feed_item: FeedItem
) -> Optional[Article]:
    """Process a single feed item for a topic."""
    # Skip if content not relevant
    if not filter_relevance(topic.name, topic.description, current_article.content, feed_content):
        debug(f"Feed item '{feed_item.url}' not relevant to topic '{topic.name}'")  # Added debug log
        return None
        
    # Update article with new content
    refined_content = refine_article(topic.name, topic.description, current_article.content, feed_content)
    updated_article = update_article(
        article_id=current_article.id,
        content=refined_content,
        feed_item=feed_item
    )
    
    info(f"Updated article for topic '{topic.name}' with content from '{feed_item.url}'")  # Added info log
    
    return updated_article

def update_topic(topic_id: str) -> Optional[Topic]:
    """Update topic article based on feed content."""
    try:
        # Load topic
        topic = get_topic(topic_id)
        if not topic:
            warning(f"Topic {topic_id} not found")  # Added warning log
            raise HTTPException(status_code=404, detail="Topic not found")
                
        # Process feeds
        info(f"Updating topic '{topic.name}'")  # Added info log
        user_info(f"Searching for new content for topic: {topic.name}")  # Added user-facing log
        
        for feed_url in topic.feed_urls:
            info(f"Processing feed {feed_url}")  # Changed from print to info
            news_feed_update_requested.send(topic, feed_url=feed_url)
        return topic
        
    except Exception as e:
        error(f"Error updating topic: {str(e)}")  # Changed from print to error
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 
    
    