from fastapi import HTTPException
from api.models.topic import Topic
from api.models.article import Article
from api.db.topic_db import get_topic, save_topic
from api.db.article_db import get_article, update_article, create_article
from api.models.feed_item import FeedItem
from typing import Optional, Dict, Any
from api.signals import topic_update_requested, news_feed_update_requested, news_feed_item_found, publish_requested, article_updated, convert_requested, article_generation_requested
from utils.logging import debug, info, warning, error
import threading
from queue import Queue
import news.feeds
import news.publishers
import news.converter   
import time

# Import the Runnable steps directly
from curator.steps import InputCreatorStep, RelevanceFilterStep, ArticleRefinerStep, ResultProcessorStep, ArticleGeneratorStep

# Add queue for handling updates
update_queue = Queue()
feed_item_queue = Queue()  # New queue for feed items

def handle_topic_update(sender, topic_id):
    """Signal handler for topic update requests."""
    update_queue.put(topic_id)
    debug("TOPIC", "Update queued", f"ID: {topic_id}, Sender: {sender}")

def handle_topic_publishing(sender):
    """Signal handler for topic publishing requests."""
    info("TOPIC", "Publishing", sender.name)
    
    # Process feeds
    topic = sender
    for publish_url in topic.publish_urls:
        # split publish_url into piped elements
        commands = [cmd.strip() for cmd in publish_url.split('|')]

        debug("CONVERT", "Default conversion", "content")
        convert_requested.send(topic, type="content")

        for cmd in commands:
            if cmd.startswith('convert://'):
                conversion_type = cmd.split('://', 1)[1].strip()
                info("CONVERT", conversion_type, f"Topic: {topic.name}")
                convert_requested.send(topic, type=conversion_type)
            else:
                info("PUBLISH", cmd, f"Topic: {topic.name}")
                publish_requested.send(topic, publish_url=cmd)

def handle_article_generation(sender, topic_id: str, topic_name: str, topic_description: str):
    """Signal handler for article generation requests."""
    try:
        # Get the topic
        topic = get_topic(topic_id)
        if not topic:
            warning("ARTICLE", "Topic not found", f"ID: {topic_id}, Name: {topic_name}")
            return
            
        chain = create_curator_chain()
        
        # Execute the chain with just the topic
        chain.invoke({"topic": topic})
        
    except Exception as e:
        error("ARTICLE", "Generation failed", f"{topic_name}: {str(e)}")

def process_update_queue():
    """Process queued topic updates and feed items."""
    while True:
        try:
            # Check for pending topic updates
            if not update_queue.empty():
                topic_id = update_queue.get()
                debug("TOPIC", "Processing update", topic_id)
                update_topic(topic_id)
            
            # Check for pending feed items
            if not feed_item_queue.empty():
                feed_item_data = feed_item_queue.get()
                process_queued_feed_item(feed_item_data)
            
            # Small sleep to prevent CPU spinning
            if update_queue.empty() and feed_item_queue.empty():
                time.sleep(0.1)
                
        except Exception as e:
            error("SYSTEM", "Queue processing error", str(e))

def process_queued_feed_item(feed_item_data):
    """Process a feed item from the queue."""
    try:
        feed_item = feed_item_data['feed_item']
        debug("FEED", "Processing item", feed_item.url)
        handle_feed_item(
            sender=feed_item_data['sender'],
            feed_url=feed_item_data['feed_url'],
            feed_item=feed_item_data['feed_item'],
            content=feed_item_data['content']
        )
    except Exception as e:
        error("FEED", "Processing error", str(e))

def handle_feed_item(sender, feed_url: str, feed_item: FeedItem, content: str):
    """Signal handler for feed item found."""
    debug("FEED", "Item found", f"{feed_url} ({feed_item.url})")

    # If this item needs further processing, send a new feed update request
    if feed_item.needs_further_processing:
        debug("FEED", "Further processing needed", feed_item.url)
        news_feed_update_requested.send(sender, feed_url=feed_item.url)
        return

    topic = sender
    processed_items = {(item.url, item.content_hash): item for item in topic.processed_feeds}

    # Skip if already processed
    if (feed_item.url, feed_item.content_hash) in processed_items:
        debug("FEED", "Skipping processed item", feed_item.url)
        return

    # Process feed item through the curator chain
    process_feed_item(topic, content, feed_item)
        
    # Publish updated article if content was relevant
    if feed_item.is_relevant:
        article_updated.send(topic)

def queue_feed_item(sender, feed_url: str, feed_item: FeedItem, content: str):
    """Queue a feed item for processing."""
    debug("FEED", "Queuing item", feed_item.url)
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
    info("SYSTEM", "Content processor started", "Topic updater ready")
    
    return processor_thread

def create_curator_chain():
    """Create the LCEL curator chain."""
    # Initialize step components
    input_creator = InputCreatorStep()
    article_generator = ArticleGeneratorStep()
    relevance_filter = RelevanceFilterStep()
    article_refiner = ArticleRefinerStep()
    result_processor = ResultProcessorStep()
    
    # Create the LCEL chain
    chain = (
        input_creator 
        | article_generator
        | relevance_filter 
        | article_refiner 
        | result_processor
    )
    
    return chain

def process_feed_item(
    topic: Topic,
    feed_content: str,
    feed_item: FeedItem
) -> Dict[str, Any]:
    """
    Process a single feed item for a topic through the curator chain.
    
    Args:
        topic: The topic being processed
        feed_content: The content from the feed
        feed_item: The feed item being processed
        
    Returns:
        Dict: The result of processing the feed item
    """
    chain = create_curator_chain()
    
    # Execute the chain
    result = chain.invoke(
        {
            "topic": topic,
            "feed_content": feed_content,
            "feed_item": feed_item
        }
    )
    
    return result

def update_topic(topic_id: str) -> Optional[Topic]:
    """Update topic article based on feed content."""
    try:
        # Load topic
        topic = get_topic(topic_id)
        if not topic:
            warning("TOPIC", "Not found", topic_id)
            raise HTTPException(status_code=404, detail="Topic not found")
                        
        # Process feeds
        info("TOPIC", "Updating", topic.name)
        
        for feed_url in topic.feed_urls:
            info("FEED", "Processing", f"URL: {feed_url}, Topic: {topic.name}")
            news_feed_update_requested.send(topic, feed_url=feed_url)
        return topic
        
    except Exception as e:
        error("TOPIC", "Update error", f"{topic_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 
    
    