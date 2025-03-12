"""
Input creator step for the curator chain.
"""
from langchain.schema.runnable import Runnable
from typing import Dict, Any

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from utils.logging import warning
from api.db.article_db import get_article
from utils.logging import debug
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
        debug("CURATOR", "Preparing curating inputs")
        
        # Extract the model objects from the input
        topic : Topic = inputs.get("topic")
        
        # Get the current article if one exists
        if not topic.article:
            return inputs
        
        article = get_article(topic.article)
        if not article:
            warning("CURATOR", "Referenced article not found", f"Topic: {topic.name}, Article ID: {topic.article}")
            inputs["should_stop"] = True
        return {
                **inputs,
                "existing_article": article,
            }             
