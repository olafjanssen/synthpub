"""
Article generator step for the curator workflow.

This module handles generating new articles for topics that don't have one yet.
"""
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional, Callable

from api.models.topic import Topic
from services.llm_service import get_llm
from api.db.prompt_db import get_prompt
from api.db.article_db import create_article
from api.db.topic_db import save_topic
from utils.logging import info, error, debug
from api.models.article import Article

def should_generate(true_node: str = "generate_article", false_node: str = "news_relevance", error_node: str = "end") -> Callable[[Dict[str, Any]], str]:
    """
    Create a routing function that decides if we need to generate a new article.
    
    Args:
        true_node: Node to route to if article needs to be generated
        false_node: Node to route to if article exists
        error_node: Node to route to if there's an error
    
    Returns:
        A function that takes state and returns the next node identifier
    """
    def _should_generate_router(state: Dict[str, Any]) -> str:
        """Inner function that evaluates the state and returns the next node."""
        if state.get("has_error", False):
            debug("CURATOR", "Stopping due to error", state.get("error_message", "Unknown error"))
            return error_node
            
        if not state.get("existing_article"):
            debug("CURATOR", "No existing article, need to generate one")
            return true_node
        
        debug("CURATOR", "Article exists, checking relevance")
        return false_node
        
    return _should_generate_router

def process(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a new article if one doesn't exist for the topic.
    
    Args:
        state: Current workflow state with topic and existing_article
        
    Returns:
        Updated state with generated_article if one was created
    """
    # Create a new state starting with the current state
    new_state = {**state}
    
    # Extract the topic from state
    topic = state.get("topic")
    
    # By the time we reach this step, we assume the graph structure ensures:
    # 1. The topic exists
    # 2. There's no existing article
    
    # Generate a new article
    try:
        # Generate the article
        new_article = generate_article(topic)
        
        # Update the state with the new article
        new_state["generated_article"] = new_article
        new_state["existing_article"] = new_article
        
        return new_state
    except Exception as e:
        error_message = str(e)
        error("GENERATOR", "Failed to generate article", error_message)
        new_state["has_error"] = True
        new_state["error_message"] = f"Failed to generate article: {error_message}"
        new_state["error_step"] = "article_generator"
        return new_state

def generate_article(topic: Topic) -> Article:
    """
    Generate a new article for the topic.
    
    Args:
        topic: The topic to generate an article for
        
    Returns:
        The generated article
    
    Raises:
        Exception: If article generation fails
    """
    topic_title = topic.name
    topic_description = topic.description
    
    # Get the LLM
    llm = get_llm('article_generation')
    
    # Get the prompt template from the database
    prompt_data = get_prompt('article-generation')
    if not prompt_data:
        raise ValueError("Article generation prompt not found in the database")
    
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
    
    return new_article