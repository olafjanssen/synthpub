from fastapi import HTTPException
from api.models.topic import Topic
from api.models.article import Article
from api.db.topic_db import get_topic
from api.db.article_db import get_article, update_article
from curator.article_relevance_filter import filter_relevance
from curator.article_refiner import refine_article
from api.models.feed_item import FeedItem
from typing import Optional
from api.signals import topic_update_requested, topic_updated, news_feed_update_requested, news_feed_item_found, publish_requested, article_updated, convert_requested
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
    print(f"Queued update request for topic {topic_id} from {sender}")

def handle_topic_publishing(sender):
    """Signal handler for topic publishing requests."""
    print(f"Publishing topic {sender.id}")
    
    # Process feeds
    topic = sender
    for publish_url in topic.publish_urls:
        # split publish_url into piped elements
        commands = [cmd.strip() for cmd in publish_url.split('|')]

        print("Default conversion: content")
        convert_requested.send(topic, type="content")

        for cmd in commands:
            if cmd.startswith('convert://'):
                print(f"Converting to {cmd}")
                convert_requested.send(topic, type=cmd.split('://', 1)[1].strip())
            else:
                print(f"Publishing to {cmd}")
                publish_requested.send(topic, publish_url=cmd)


def process_update_queue():
    """Process queued topic updates and feed items."""
    while True:
        try:
            # Check for pending topic updates
            if not update_queue.empty():
                topic_id = update_queue.get()
                print(f"Processing update for topic {topic_id}")
                update_topic(topic_id)
            
            # Check for pending feed items
            if not feed_item_queue.empty():
                feed_item_data = feed_item_queue.get()
                process_queued_feed_item(feed_item_data)
            
            # Small sleep to prevent CPU spinning
            if update_queue.empty() and feed_item_queue.empty():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error processing queue item: {str(e)}")

def process_queued_feed_item(feed_item_data):
    """Process a feed item from the queue."""
    try:
        print(f"Processing feed item: {feed_item_data['feed_item'].url}")
        handle_feed_item(
            sender=feed_item_data['sender'],
            feed_url=feed_item_data['feed_url'],
            feed_item=feed_item_data['feed_item'],
            content=feed_item_data['content']
        )
    except Exception as e:
        print(f"Error processing feed item: {str(e)}")

def handle_feed_item(sender, feed_url: str, feed_item: FeedItem, content: str):
    """Signal handler for feed item found."""
    print(f"Feed item found for {feed_url}: {feed_item.url}")

    # If this item needs further processing, send a new feed update request
    if feed_item.needs_further_processing:
        print(f"Item needs further processing: {feed_item.url}")
        news_feed_update_requested.send(sender, feed_url=feed_item.url)
        return

    topic = sender
    processed_items = {(item.url, item.content_hash): item for item in topic.processed_feeds}

    # Skip if already processed
    if (feed_item.url, feed_item.content_hash) in processed_items:
        print(f"Skipping feed item {feed_item.url} as it has already been processed")
        return

    current_article = get_article(topic.article)
    if not current_article:
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

    # Save updated topic
    topic_updated.send(topic)

    # Publish updated article
    if updated_article:
        article_updated.send(topic)

def queue_feed_item(sender, feed_url: str, feed_item: FeedItem, content: str):
    """Queue a feed item for processing."""
    print(f"Queuing feed item: {feed_item.url}")
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
    
    # Start queue processor thread
    processor_thread = threading.Thread(target=process_update_queue, daemon=True)
    processor_thread.start()
    print("Topic update processor started")

def process_feed_item(
    topic: Topic,
    current_article: Article,
    feed_content: str,
    feed_item: FeedItem
) -> Optional[Article]:
    """Process a single feed item for a topic."""
    # Skip if content not relevant
    if not filter_relevance(topic.name, topic.description, current_article.content, feed_content):
        return None
        
    # Update article with new content
    refined_content = refine_article(topic.name, topic.description, current_article.content, feed_content)
    updated_article = update_article(
        article_id=current_article.id,
        content=refined_content,
        feed_item=feed_item
    )
    
    return updated_article

def update_topic(topic_id: str) -> Optional[Topic]:
    """Update topic article based on feed content."""
    try:
        # Load topic
        topic = get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
                
        # Process feeds
        for feed_url in topic.feed_urls:
            print(f"Processing feed {feed_url}")
            news_feed_update_requested.send(topic, feed_url=feed_url)
        return topic
        
    except Exception as e:
        print(f"Error updating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 
    
    