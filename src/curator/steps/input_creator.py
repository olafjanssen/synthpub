"""
Input creator step for the curator chain.
"""
from langchain.schema.runnable import Runnable
from typing import Dict, Any

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem

class InputCreatorStep(Runnable):
    """Runnable step that creates the input dictionary for the chain."""
    
    def invoke(self, inputs: Dict[str, Any], config=None) -> Dict[str, Any]:
        """
        Create a dictionary with all input values needed for the chain.
        
        Args:
            inputs: Dictionary with topic, article, and feed content
            config: Optional configuration for the runnable
            
        Returns:
            Dictionary with all necessary inputs for downstream steps
        """
        topic = inputs["topic"]
        current_article = inputs["current_article"]
        feed_content = inputs["feed_content"]
        feed_item = inputs["feed_item"]
        
        return {
            "topic_title": topic.name,
            "topic_description": topic.description,
            "article": current_article.content,
            "new_context": feed_content,
            "topic": topic,
            "current_article": current_article,
            "feed_content": feed_content,
            "feed_item": feed_item
        } 