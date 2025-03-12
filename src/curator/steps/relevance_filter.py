"""
Relevance filter step for the curator chain.
"""
from langchain.schema.runnable import Runnable
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Tuple

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from curator.llm_utils import get_llm
from api.db.prompt_db import get_prompt
from utils.logging import debug, info

class RelevanceResponse(BaseModel):
    """Model for the relevance filter response."""
    is_relevant: bool = Field(description="Whether the new content is relevant to the topic or article")
    explanation: str = Field(description="Explanation of why the content is or is not relevant")

class RelevanceFilterStep(Runnable):
    """Runnable step that filters content for relevance to topic."""
    
    def _filter_relevance(self, topic_title: str, topic_description: str, article: str, new_context: str) -> Tuple[bool, str]:
        """
        Determine if new context is relevant to the existing article.
        
        Args:
            topic_title: Title of the topic to write about
            topic_description: Description and context for the topic to write about
            article: Current article text
            new_context: New text to evaluate
            
        Returns:
            bool: True if the new context is relevant
            str: Explanation of why the content is or is not relevant
        """
        # Get the prompt template from the database
        prompt_data = get_prompt('article-relevance-filter')
        if not prompt_data:
            raise ValueError("Article relevance filter prompt not found in the database")
        
        # Create a Pydantic output parser
        parser = PydanticOutputParser(pydantic_object=RelevanceResponse)
        
        # Create the prompt template with format instructions as partial variables
        prompt = PromptTemplate(
            template=prompt_data.template + "\n\n{format_instructions}",
            input_variables=["topic_title", "topic_description", "article", "new_context"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
            
        # Format the prompt with our variables
        formatted_prompt = prompt.format(
            topic_title=topic_title,
            topic_description=topic_description,
            article=article,
            new_context=new_context
        )
            
        # Get the LLM and invoke it
        llm = get_llm('article_refinement')
        response_text = llm.invoke(formatted_prompt).content
        
        try:
            # Parse the response into the Pydantic model
            parsed_response = parser.parse(response_text)
            debug("FILTER", "Parsed Response", f"is_relevant: {parsed_response.is_relevant}, explanation: {parsed_response.explanation}")
            return (parsed_response.is_relevant, parsed_response.explanation)
        except Exception as e:
            # Fallback to the original parsing method if the structured parsing fails
            debug("FILTER", "Parsing Error", str(e))
            is_relevant = "YES" in response_text.strip().upper()
            return is_relevant, response_text.strip()
    
    def invoke(self, inputs: Dict[str, Any], config=None) -> Dict[str, Any]:
        """
        Process inputs through the relevance filter step.
        
        Args:
            inputs: Dictionary with topic, article, and feed content information
            config: Optional configuration for the runnable
            
        Returns:
            Dictionary with original inputs and relevance information added
        """
        topic_title = inputs["topic_title"]
        topic_description = inputs["topic_description"]
        article = inputs["article"]
        new_context = inputs["new_context"]
        feed_item = inputs["feed_item"]
        
        is_relevant, explanation = self._filter_relevance(
            topic_title, 
            topic_description, 
            article, 
            new_context
        )
        
        # Store explanation in feed item
        feed_item.relevance_explanation = explanation
        
        if not is_relevant:
            debug("CURATOR", "Content not relevant", 
                  f"Topic: {topic_title}, Item: {feed_item.url}")
        else:
            info("CURATOR", "Content is relevant", 
                 f"Topic: {topic_title}, Item: {feed_item.url}")
        
        # Pass both the result and the inputs to the next step
        return {
            **inputs,
            "is_relevant": is_relevant,
            "relevance_explanation": explanation
        } 