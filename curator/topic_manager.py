"""Topic management and update logic."""
from typing import Optional, List, Tuple, Dict
from api.models.topic import Topic, TopicCreate
from api.models.article import Article
from api.models.feed_item import FeedItem
from .article_generator import generate_article
from .feeds.feed_processor import process_feeds
from .article_refiner import refine_article

def create_new_topic(
    topic: TopicCreate,
    create_article_fn,
    topic_id: str
) -> Tuple[str, Topic]:
    """
    Create a new topic with initial article.
    
    Args:
        topic: Topic creation data
        create_article_fn: Function to create article in database
        topic_id: Pre-generated topic ID
        
    Returns:
        Tuple of (article_id, topic)
    """
    # Generate initial article content
    content = generate_article(topic.description)
    
    # Create article
    article = create_article_fn(
        title=topic.name,
        topic_id=topic_id,
        content=content
    )
    
    # Create topic object
    topic_data = Topic(
        id=topic_id,
        name=topic.name,
        description=topic.description,
        article=article.id,
        feed_urls=topic.feed_urls
    )
    
    return article.id, topic_data

def process_topic_updates(
    topic: Topic,
    current_article: Article,
    update_article_fn
) -> Tuple[Optional[Article], List[FeedItem]]:
    """
    Process feed updates for a topic.
    
    Args:
        topic: Topic to update
        current_article: Current version of article
        update_article_fn: Function to update article in database
        
    Returns:
        Tuple of (updated_article, new_feed_items)
    """
    # Process feeds
    feed_contents, feed_items = process_feeds(topic.feed_urls)
    
    # Create lookup of processed items
    processed_items = {
        (item.url, item.content_hash): item 
        for item in topic.processed_feeds
    }
    
    # Filter new content
    new_content_pairs = [
        (content, feed_item) 
        for content, feed_item in zip(feed_contents, feed_items)
        if (feed_item.url, feed_item.content_hash) not in processed_items
    ]
    
    if not new_content_pairs:
        return None, []
    
    # Update article with new content
    refined_content = current_article.content
    updated_article = current_article
    
    for content, feed_item in new_content_pairs:
        refined_content = refine_article(refined_content, content)
        updated_article = update_article_fn(
            article_id=updated_article.id,
            content=refined_content,
            feed_item=feed_item
        )
        if not updated_article:
            raise ValueError("Failed to update article")
            
    return updated_article, feed_items 