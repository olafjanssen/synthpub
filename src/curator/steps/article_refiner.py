"""
Article refiner step for the curator chain.
"""
from langchain.schema.runnable import Runnable
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from curator.llm_utils import get_llm
from api.db.prompt_db import get_prompt
from api.db.article_db import update_article
from utils.logging import info, error

class ArticleRefinerStep(Runnable):
    """Runnable step that refines article content if relevant."""
    
    def invoke(self, inputs: Dict[str, Any], config=None) -> Dict[str, Any]:
        """
        Process inputs through the article refiner step.
        
        Args:
            inputs: Dictionary with topic, article, feed content and relevance information
            config: Optional configuration for the runnable
            
        Returns:
            Dictionary with original inputs and refined content added
        """
        # Skip refinement if content is not relevant
        if not inputs["is_relevant"]:
            return inputs
        
        topic_title = inputs["topic_title"]
        topic_description = inputs["topic_description"]
        article = inputs["article"]
        new_context = inputs["new_context"]
        feed_item = inputs["feed_item"]
        current_article = inputs["current_article"]
        
        try:
            # Get the LLM
            llm = get_llm('article_refinement')
            
            # Get the prompt template from the database
            prompt_data = get_prompt('article-refinement')
            if not prompt_data:
                raise ValueError("Article refinement prompt not found in the database")
            
            # Create and format the prompt
            prompt = PromptTemplate.from_template(prompt_data.template)
            
            # Invoke the LLM to refine the article
            refined_content = llm.invoke(prompt.format(
                topic_title=topic_title,
                topic_description=topic_description,
                article=article,
                new_context=new_context
            )).content
            
            # Update the article in the database
            updated_article = update_article(
                article_id=current_article.id,
                content=refined_content,
                feed_item=feed_item
            )
            
            info("CURATOR", "Article refined", 
                 f"Topic: {topic_title}, Source: {feed_item.url}")
            
            return {
                **inputs,
                "refined_content": refined_content,
                "success": True
            }
        except Exception as e:
            error("CURATOR", "Failed to refine article", str(e))
            return {
                **inputs,
                "refined_content": None,
                "success": False
            } 