"""
Article generator step for the curator chain.
"""
from langchain.schema.runnable import Runnable
from langchain.prompts import PromptTemplate
from typing import Dict, Any

from api.models.topic import Topic
from services.llm_service import get_llm
from api.db.prompt_db import get_prompt
from api.db.article_db import create_article
from api.db.topic_db import save_topic
from utils.logging import info, error, debug
from api.models.article import Article
from curator.steps.chain_errors import ChainStopError

class ArticleGeneratorStep(Runnable):
    """Runnable step that generates a new article if one doesn't exist yet."""
    
    def invoke(self, inputs: Dict[str, Any], config=None) -> Dict[str, Any]:
        """
        Process inputs through the article generator step.
        
        Args:
            inputs: Dictionary with topic information
            config: Optional configuration for the runnable
            
        Returns:
            Dictionary with original inputs and possibly a new article
        """

        # Extract the model objects from the input
        topic : Topic = inputs["topic"]
        article : Article = inputs["existing_article"]

        info("GENERATOR", "Article:", article)

        # Skip generation if the topic already has an article
        if article:
            debug("GENERATOR", "Article already exists", f"Topic: {topic.name}")
            return inputs
        
        topic_title = topic.name
        topic_description = topic.description
        
        try:
            # Get the LLM
            llm = get_llm('article_generation')
            
            # Get the prompt template from the database
            prompt_data = get_prompt('article-generation')
            if not prompt_data:
                raise ChainStopError("Article generation prompt not found in the database", step="article_generator", topic=topic)
            
            # Create and format the prompt
            prompt = PromptTemplate.from_template(prompt_data.template)
            
            # Invoke the LLM to generate the article
            info("GENERATOR", "Generating article", f"Topic: {topic_title}")
            content = llm.invoke(prompt.format(
                topic_title=topic_title,
                topic_description=topic_description
            )).content
            
            # Create article in the database
            new_article = create_article(
                title=topic_title,
                topic_id=topic.id,
                content=content
            )
            
            # Update the topic with the new article ID
            topic.article = new_article.id
            save_topic(topic)
            
            info("GENERATOR", "Article generated", f"Topic: {topic_title}")
            
            return {
                **inputs,
                "generated_article": new_article,
                "existing_article": new_article
            }
        except Exception as e:
            error("GENERATOR", "Failed to generate article", str(e))
            raise ChainStopError(f"Failed to generate article: {str(e)}", step="article_generator", topic=topic)