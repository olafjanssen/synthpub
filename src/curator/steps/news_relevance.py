"""
News relevance step for the curator workflow.

This module checks if new content is relevant to an existing topic and article.
"""
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any, Callable

from services.llm_service import get_llm
from api.db.prompt_db import get_prompt
from api.db.topic_db import save_topic
from utils.logging import debug, warning, error

class RelevanceResponse(BaseModel):
    """Model for the relevance filter response."""
    is_relevant: bool = Field(description="Whether the new content is relevant to the topic or article")
    explanation: str = Field(description="Explanation of why the content is or is not relevant")

def is_relevant(true_node: str, false_node: str) -> Callable[[Dict[str, Any]], str]:
    """
    Create a routing function that decides if the content is relevant to the topic.
    
    Args:
        true_node: Node to route to if content is relevant
        false_node: Node to route to if content is not relevant
        error_node: Node to route to if there's an error
    
    Returns:
        A function that takes state and returns the next node identifier
    """
    def _is_relevant_router(state: Dict[str, Any]) -> str:
        """Inner function that evaluates the state and returns the next node."""

        feed_item = state.get("feed_item")
        if not feed_item or not feed_item.is_relevant:
            debug("CURATOR", "Content not relevant, stopping workflow")
            return false_node
        
        debug("CURATOR", "Content relevant, proceeding to article refinement")
        return true_node
    
    return _is_relevant_router

def process(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if feed content is relevant to the topic and article.
    
    Args:
        state: Current workflow state with topic, article, and feed content
        
    Returns:
        Updated state with is_relevant flag
    """
    # Create a new state starting with the current state
    new_state = {**state}
    
    # Extract needed data from state
    topic = state.get("topic")
    article = state.get("existing_article")
    feed_content = state.get("feed_content")
    feed_item = state.get("feed_item")
    
    # By the time we reach this step, we assume the graph structure ensures:
    # 1. We have a topic
    # 2. We have an article (either existing or newly generated)
    # 3. We have feed content to check
                    
    # Log that we're checking relevance
    debug("CURATOR", "Checking relevance", f"Topic: {topic.name}, Feed: {feed_item.url}")
    
    try:
        # Get the relevance determination from LLM
        relevance_result = determine_relevance(
            topic_title=topic.name,
            topic_description=topic.description,
            article_content=article.content,
            feed_content=feed_content
        )
            
        debug("CURATOR", f"Content relevance: {relevance_result.is_relevant}", 
              f"Topic: {topic.name}, Reason: {relevance_result.explanation}")
        
        # Update feed item with relevance information
        feed_item.is_relevant = relevance_result.is_relevant
        feed_item.relevance_explanation = relevance_result.explanation
        
        # Add to processed feeds and save topic
        topic.processed_feeds.append(feed_item)
        save_topic(topic)
        
        # If content is not relevant, add explanation but don't set has_error
        if not relevance_result.is_relevant:
            new_state["error_message"] = relevance_result.explanation
            new_state["error_step"] = "news_relevance"
        
        return new_state
        
    except Exception as e:
        error_message = str(e)
        error("CURATOR", "Failed to check relevance", error_message)
        new_state["has_error"] = True
        new_state["error_message"] = f"Failed to check relevance: {error_message}"
        new_state["error_step"] = "news_relevance"
        return new_state

def determine_relevance(
    topic_title: str, 
    topic_description: str,
    article_content: str,
    feed_content: str
) -> RelevanceResponse:
    """
    Determine if feed content is relevant to a topic and article.
    
    Args:
        topic_title: The title of the topic
        topic_description: The description of the topic
        article_content: The current article content
        feed_content: The new feed content to check
        
    Returns:
        A RelevanceResponse with the relevance determination
        
    Raises:
        Exception: If the relevance check fails
    """
    # Get the LLM
    llm = get_llm('relevance_filter')
    
    # Get the prompt template from the database
    prompt_data = get_prompt('article-relevance-filter')
    if not prompt_data:
        warning("CURATOR", "Prompt not found", "article-relevance-filter prompt not found in database")
        # Return a default "not relevant" response
        return RelevanceResponse(
            is_relevant=False,
            explanation="Unable to determine relevance: prompt template not found"
        )
        
    # Set up the parser
    parser = PydanticOutputParser(pydantic_object=RelevanceResponse)
            
    # Create the prompt with format instructions
    prompt = PromptTemplate(
        template=prompt_data.template + "\n\n {format_instructions}",
        input_variables=["topic_title", "topic_description", "article", "new_context"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Create and invoke the relevance chain
    relevance_chain = prompt | llm | parser
    return relevance_chain.invoke({
        "topic_title": topic_title,
        "topic_description": topic_description,
        "article": article_content,
        "new_context": feed_content
    }) 
