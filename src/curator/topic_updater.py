from fastapi import HTTPException
from api.models.topic import Topic
from api.models.article import Article
from api.db.topic_db import get_topic, save_topic
from api.db.article_db import get_article, update_article
from curator.feeds.feed_processor import process_feeds
from typing import Optional

def update_topic(topic_id: str) -> Optional[Topic]:
    """Update topic article based on feed content."""
    try:
        # Load topic
        topic = get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        current_article = get_article(topic.article)
        if not current_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Process feeds
        feed_contents, feed_items = process_feeds(topic.feed_urls)
        processed_items = {(item.url, item.content_hash): item for item in topic.processed_feeds}
        
        # Process each feed item
        for content, feed_item in zip(feed_contents, feed_items):
            # Skip if already processed
            if (feed_item.url, feed_item.content_hash) in processed_items:
                continue
            
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
                current_article = updated_article
                topic.article = updated_article.id
        
            # Save updated topic
            save_topic(topic)
        return topic
        
    except Exception as e:
        print(f"Error updating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 