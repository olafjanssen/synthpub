"""
Article refiner step for the curator workflow.

This module refines existing articles with new relevant content.
"""
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from services.llm_service import get_llm
from api.db.prompt_db import get_prompt
from api.db.article_db import update_article
from utils.logging import info, error, debug
from api.db.topic_db import save_topic

def process(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refine an existing article with new relevant content.
    
    Args:
        state: Current workflow state with topic, article, and feed content
        
    Returns:
        Updated state with refined_article
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
    # 2. We have an article to refine
    # 3. We have relevant feed content
    # 4. We have a feed item
    
    try:
        # Refine the article with the new content
        refined_article = refine_article(
            topic=topic,
            current_article=article,
            feed_content=feed_content,
            feed_item=feed_item
        )
        
        # Update state with refined article
        new_state["refined_article"] = refined_article
        
        return new_state
        
    except Exception as e:
        error_message = str(e)
        error("CURATOR", "Failed to refine article", error_message)
        new_state["has_error"] = True
        new_state["error_message"] = f"Failed to refine article: {error_message}"
        new_state["error_step"] = "article_refiner"
        return new_state

def refine_article(
    topic: Topic,
    current_article: Article,
    feed_content: str,
    feed_item: FeedItem
) -> Article:
    """
    Refine an article with new content.
    
    Args:
        topic: The topic the article belongs to
        current_article: The current article to refine
        feed_content: The new content to incorporate
        feed_item: The feed item that provided the content
        
    Returns:
        The refined article
        
    Raises:
        Exception: If article refinement fails
    """
    # Get the LLM
    llm = get_llm('article_refinement')
    
    # Get the prompt template from the database
    prompt_data = get_prompt('article-refinement')
    if not prompt_data:
        raise ValueError("Article refinement prompt not found in the database")
    
    # Create and format the prompt
    prompt = PromptTemplate.from_template(prompt_data.template)
    
    # Invoke the LLM to refine the article
    debug("REFINER", "Refining article", f"Topic: {topic.name}, Source: {feed_item.url}")
    refined_content = llm.invoke(prompt.format(
        topic_title=topic.name,
        topic_description=topic.description,
        article=current_article.content,
        new_context=feed_content
    )).content
    
    # Update the article in the database
    updated_article = update_article(
        article_id=current_article.id,
        content=refined_content,
        feed_item=feed_item
    )
    
    # Update the topic reference and save
    topic.article = updated_article.id
    save_topic(topic)

    info("CURATOR", "Article refined", 
         f"Topic: {topic.name}, Source: {feed_item.url}")
    
    return updated_article 