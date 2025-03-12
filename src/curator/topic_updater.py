from fastapi import HTTPException
from api.models.topic import Topic
from api.models.feed_item import FeedItem
from typing import Optional, Dict, Any
from api.signals import topic_update_requested, publish_requested, convert_requested
from utils.logging import debug, info, warning, error
import threading
from queue import Queue
import news.feeds
import news.publishers
import news.converter   
import time
from api.db.topic_db import get_topic, save_topic
from api.db.article_db import get_article, update_article, create_article
from api.db.cache_manager import get_all_connectors

# Import the Runnable steps directly
from curator.steps import InputCreatorStep, RelevanceFilterStep, ArticleRefinerStep, ArticleGeneratorStep
from curator.steps.chain_errors import ChainStopError

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
    """Handler for feed items."""
    debug("FEED", "Item found", f"{feed_url} ({feed_item.url})")

    # If this item needs further processing, process it directly with connectors
    if feed_item.needs_further_processing:
        debug("FEED", "Further processing needed", feed_item.url)
        process_feed_url(sender, feed_item.url)
        return

    topic = sender

    # Process feed item through the curator chain
    process_feed_item(topic.id, content, feed_item)
    
    # Always trigger publishing after processing
    handle_topic_publishing(topic)

def add_feed_item_to_queue(sender, feed_url: str, feed_item: FeedItem, content: str):
    """Add a feed item to the processing queue."""
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
    
    # Create the LCEL chain
    chain = (
        input_creator 
        | article_generator
        | relevance_filter 
        | article_refiner 
    )
    
    return chain

def process_feed_item(
    topic_id: str,
    feed_content: str = None,
    feed_item: FeedItem = None
) -> None:
    """
    Process a single feed item for a topic through the curator chain.
    
    Args:
        topic: The topic being processed
        feed_content: The content from the feed
        feed_item: The feed item being processed
    """
    chain = create_curator_chain()
    
    # Execute the chain
    try:
        chain.invoke(
            {
                "topic_id": topic_id,
                "feed_content": feed_content,
                "feed_item": feed_item
            }
        )
    except ChainStopError as e:
        debug("CURATOR", "Chain stopped", f"Reason: {e.message}")
    except Exception as e:
        error("CURATOR", "Error processing feed item", str(e))

def process_feed_url(sender, feed_url: str):
    """
    Process a feed URL directly using available connectors.
    
    Args:
        sender: The topic or other object that requested the feed processing
        feed_url: The URL to process
    """
    debug("FEED", "Processing URL", feed_url)
    
    # Get all available connectors
    connectors = get_all_connectors()
    
    # Find a connector that can handle this URL
    for connector_class in connectors:
        if connector_class.can_handle(feed_url):
            debug("FEED", "Using connector", f"{connector_class.__name__} for {feed_url}")
            try:
                # Directly call the handler method that was previously triggered by the signal
                connector_class.handle_feed_update(sender, feed_url)
                return
            except Exception as e:
                error("FEED", "Connector error", f"{connector_class.__name__}: {str(e)}")
    
    warning("FEED", "No connector found", f"URL: {feed_url}")

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
            process_feed_url(topic, feed_url)
        return topic
        
    except Exception as e:
        error("TOPIC", "Update error", f"{topic_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 
    
    