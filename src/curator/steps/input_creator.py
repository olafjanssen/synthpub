"""
Input creator step for the curator chain.
"""
from langchain.schema.runnable import Runnable
from typing import Dict, Any

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from utils.logging import warning, debug
from api.db.article_db import get_article
from api.db.topic_db import get_topic
from curator.steps.chain_errors import ChainStopError

class InputCreatorStep(Runnable):
    """Runnable step that creates the input dictionary for the chain."""
    
    def invoke(self, inputs: Dict[str, Any], config=None) -> Dict[str, Any]:
        """
        Create a dictionary with all input values needed for the chain.
        
        Args:
            inputs: Dictionary with topic_id, feed_content, and feed_item
            config: Optional configuration for the runnable
            
        Returns:
            Dictionary with all necessary inputs for downstream steps
        """
        debug("CURATOR", "Preparing curating inputs")
        
        # Extract the topic_id from the input
        topic_id = inputs.get("topic_id")
        if not topic_id:
            raise ChainStopError("No topic_id provided", step="input_creator")
            
        # Load the topic from the database
        topic = get_topic(topic_id)
        if not topic:
            raise ChainStopError(f"Topic not found: {topic_id}", step="input_creator")

        processed_items = {(item.url, item.content_hash): item for item in topic.processed_feeds}

        # Skip if already processed
        feed_item : FeedItem = inputs.get("feed_item")
        if feed_item and (feed_item.url,feed_item.content_hash) in processed_items:
            raise ChainStopError(f"Feed item already processed: {feed_item.url}", step="input_creator", topic=topic)

        # Get the current article if one exists
        article = get_article(topic.article)
        if topic.article and not article:
            warning("CURATOR", "Referenced article not found", f"Topic: {topic.name}, Article ID: {topic.article}")
            raise ChainStopError(f"Referenced article not found: {topic.article}", step="input_creator", topic=topic)
            
        return {
                **inputs,
                "topic": topic,
                "existing_article": article,
            }             
