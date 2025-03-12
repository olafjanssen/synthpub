"""
Relevance filter step for the curator chain.
"""
from langchain_core.runnables import Runnable, RunnableLambda
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from services.llm_service import get_llm
from api.db.prompt_db import get_prompt
from api.db.topic_db import save_topic
from utils.logging import debug, warning

# Import the general ChainStopError
from curator.steps.chain_errors import ChainStopError

class RelevanceResponse(BaseModel):
    """Model for the relevance filter response."""
    is_relevant: bool = Field(description="Whether the new content is relevant to the topic or article")
    explanation: str = Field(description="Explanation of why the content is or is not relevant")

class RelevanceFilterStep(Runnable):
    """Runnable step that filters content based on relevance to the topic."""
    
    def invoke(self, inputs: Dict[str, Any], config=None) -> Dict[str, Any]:
        """
        Check if feed content is relevant to the topic and article.
        
        Args:
            chain_input: Dictionary with topic, feed content, and other info
        
        Returns:
            Updated chain input with relevance flag
        """
        topic: Topic = inputs["topic"]
        existing_article : Article = inputs["existing_article"]
        feed_content : str = inputs["feed_content"]
        feed_item : FeedItem = inputs["feed_item"]
        
        # Short-circuit if feed content is empty or missing (for new topics without content)
        if not feed_content or not feed_item:
            debug("CURATOR", "Relevance filter step", f"No feed content for {topic.name}, skipping relevance check")
            raise ChainStopError("No feed content provided", feed_item=feed_item)
                        
        # Now we know we have an article and feed content
        debug("CURATOR", "Checking relevance", f"Topic: {topic.name}, Feed: {feed_item.url}")
                
        # Use LLM to determine relevance
        llm = get_llm('relevance_filter')
        
        # Get the prompt template from the database
        prompt_data = get_prompt('article-relevance-filter')
        if not prompt_data:
            warning("CURATOR", "Prompt not found", "article-relevance-filter prompt not found in database")
            raise ChainStopError("Prompt not found", feed_item=feed_item)
            
        # Set up the parser
        parser = PydanticOutputParser(pydantic_object=RelevanceResponse)
                
        prompt = PromptTemplate(
            template=prompt_data.template + "\n\n {format_instructions}",
            input_variables=["topic_title", "topic_description", "article", "new_context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        relevance_chain = prompt | llm | parser

        response = relevance_chain.invoke({
            "topic_title": topic.name,
            "topic_description": topic.description,
            "article": existing_article.content,
            "new_context": feed_content
        })
            
        debug("CURATOR", f"Content relevance: {response.is_relevant}", f"Topic: {topic.name}, Reason: {response.explanation}")
        
        # Update feed item with relevance information
        feed_item.is_relevant = response.is_relevant
        feed_item.relevance_explanation = response.explanation
        topic.processed_feeds.append(feed_item)
        
        save_topic(topic)
        
        # If content is not relevant, raise an exception to stop the chain
        if not response.is_relevant:
            raise ChainStopError(response.explanation, feed_item=feed_item, is_relevant=False)
            
        # Otherwise, continue with the chain
        return inputs 
