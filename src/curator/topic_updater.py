from fastapi import HTTPException
from api.models.topic import Topic
from api.models.feed_item import FeedItem
from typing import Optional, Dict, Any, Tuple, Union
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

# Single processing queue for all items
# Each item is a tuple (topic_id, content, feed_item)
processing_queue = Queue()

def handle_topic_update(sender, topic_id):
    """Signal handler for topic update requests."""
    try:
        # Load topic
        topic = get_topic(topic_id)
        if not topic:
            warning("TOPIC", "Not found", topic_id)
            return
        
        info("TOPIC", "Queuing update", topic.name)
        
        # Queue each feed URL as a separate item
        for feed_url in topic.feed_urls:
            # Create a feed item for the URL with needs_further_processing=True
            feed_item = FeedItem.create(url=feed_url, content="", needs_further_processing=True)
            
            # Add to queue (topic_id, content=None, feed_item)
            processing_queue.put((topic_id, None, feed_item))
            debug("TOPIC", "Feed queued", f"Topic: {topic.name}, URL: {feed_url}")
            
    except Exception as e:
        error("TOPIC", "Update error", f"{topic_id}: {str(e)}")

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

def process_queue():
    """Process items from the unified processing queue."""
    while True:
        try:
            # Get the next item from the queue
            if not processing_queue.empty():
                topic_id, content, feed_item = processing_queue.get()
                
                if feed_item.needs_further_processing:
                    # Process the feed URL
                    debug("FEED", "Processing URL", feed_item.url)
                    process_feed_url(topic_id, feed_item.url)
                else:
                    # Process through curator chain
                    debug("FEED", "Processing content", feed_item.url)
                    process_feed_item(topic_id, content, feed_item)
                    
                    # Trigger publishing after processing
                    topic = get_topic(topic_id)
                    if topic:
                        handle_topic_publishing(topic)
            else:
                # Small sleep to prevent CPU spinning
                time.sleep(0.1)
                
        except Exception as e:
            error("SYSTEM", "Queue processing error", str(e))

def add_feed_item_to_queue(topic_id : str, feed_item: FeedItem, content: str):
    """Add a feed item to the processing queue."""
        
    debug("FEED", "Queuing item", feed_item.url)
    
    # Add directly to queue using the uniform format
    processing_queue.put((topic_id, content, feed_item))

def start_update_processor():
    """Start the update processor thread."""
    # Connect signal handlers
    topic_update_requested.connect(handle_topic_update)
    
    # Start queue processor thread
    processor_thread = threading.Thread(target=process_queue, daemon=True)
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
        topic_id: The ID of the topic
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

def process_feed_url(topic_id: str, feed_url: str):
    """
    Process a feed URL directly using available connectors.
    
    Args:
        topic_id: The ID of the topic
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
                # Directly call the handler method 
                connector_class.handle_feed_update(topic_id, feed_url)
                return
            except Exception as e:
                error("FEED", "Connector error", f"{connector_class.__name__}: {str(e)}")
    
    warning("FEED", "No connector found", f"URL: {feed_url}") 
    
    