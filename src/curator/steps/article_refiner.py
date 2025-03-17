"""
Article refiner step for the curator workflow.

This module refines existing articles with new relevant content.
"""
from langchain.prompts import PromptTemplate
from typing import Dict, Any

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
    new_information = state.get("new_information")
    enforcing_information = state.get("enforcing_information")
    contradicting_information = state.get("contradicting_information")
        
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
        debug("REFINER", "Refining article", f"Topic: {topic.name}, Source: {feed_item.url}")
        refined_content = llm.invoke(prompt.format(
            topic_title=topic.name,
            topic_description=topic.description,
            article=article.content,
            new_context=feed_content,
            new_information=new_information,
            enforcing_information=enforcing_information,
            contradicting_information=contradicting_information
        )).content
        
        # Update the article in the database
        refined_article = update_article(
            article_id=article.id,
            content=refined_content,
            feed_item=feed_item
        )
        
        # Update the topic reference and save
        topic.article = refined_article.id
        
        # Store the article ID in the feed item
        feed_item.article_id = refined_article.id
        
        # Save the topic with updated feed item
        save_topic(topic)

        info("CURATOR", "Article refined", 
             f"Topic: {topic.name}, Source: {feed_item.url}")
        
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