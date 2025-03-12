"""
Article refiner step for the curator chain.
"""
from langchain.schema.runnable import Runnable
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from services.llm_service import get_llm
from api.db.prompt_db import get_prompt
from api.db.article_db import update_article
from utils.logging import info, error
from api.db.topic_db import save_topic
from curator.steps.chain_errors import ChainStopError

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
        # Extract data from model objects
        topic: Topic = inputs["topic"]
        current_article: Article = inputs["existing_article"]
        feed_content : str = inputs["feed_content"]
        feed_item : FeedItem = inputs["feed_item"]
        
        # Extract properties needed for the prompt
        topic_title = topic.name
        topic_description = topic.description
        article_content = current_article.content
        
        try:
            # Get the LLM
            llm = get_llm('article_refinement')
            
            # Get the prompt template from the database
            prompt_data = get_prompt('article-refinement')
            if not prompt_data:
                raise ChainStopError("Article refinement prompt not found in the database", step="article_refiner")
            
            # Create and format the prompt
            prompt = PromptTemplate.from_template(prompt_data.template)
            
            # Invoke the LLM to refine the article
            refined_content = llm.invoke(prompt.format(
                topic_title=topic_title,
                topic_description=topic_description,
                article=article_content,
                new_context=feed_content
            )).content
            
            # Update the article in the database
            updated_article = update_article(
                article_id=current_article.id,
                content=refined_content,
                feed_item=feed_item
            )
            topic.article = updated_article.id
            save_topic(topic)

            info("CURATOR", "Article refined", 
                 f"Topic: {topic_title}, Source: {feed_item.url}")
            
            return {
                **inputs,
                "refined_article": updated_article
            }
        except Exception as e:
            error("CURATOR", "Failed to refine article", str(e))
            raise ChainStopError(f"Failed to refine article: {str(e)}", step="article_refiner", feed_item=feed_item) 