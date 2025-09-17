"""
Article refiner step for the curator workflow.

This module refines existing articles with new relevant content.
"""

from typing import Any, Dict

from api.db.article_db import update_article
from api.db.topic_db import save_topic
from curator.template_service import template_service
from utils.logging import debug, error, info


def _handle_refinement_error(state: Dict[str, Any], e: Exception) -> Dict[str, Any]:
    """Handle errors in the refinement process."""
    error_message = str(e)
    error("CURATOR", "Failed to refine article", error_message)
    new_state = {**state}
    new_state["has_error"] = True
    new_state["error_message"] = f"Failed to refine article: {error_message}"
    new_state["error_step"] = "article_refiner"
    return new_state


def _should_use_incremental_refinement(topic, state: Dict[str, Any]) -> bool:
    """
    Determine whether to use incremental refinement based on topic configuration or state.
    
    Args:
        topic: Topic object
        state: Current workflow state
        
    Returns:
        True if incremental refinement should be used, False otherwise
    """
    # Check if topic has incremental refinement enabled
    if hasattr(topic, 'use_incremental_refinement') and topic.use_incremental_refinement:
        return True
    
    # Check if state explicitly requests incremental refinement
    if state.get('use_incremental_refinement', False):
        return True
    
    # Default to traditional refinement (incremental is opt-in only)
    return False


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
        # Check if incremental refinement is enabled
        use_incremental = _should_use_incremental_refinement(topic, state)
        
        if use_incremental:
            # Use incremental refinement approach
            debug("REFINER", "Using incremental refinement", f"Topic: {topic.name}")
            from curator.steps.incremental_article_refiner import process as incremental_process
            return incremental_process(state)
        
        # Use traditional refinement approach
        # Determine which template to use for refinement
        # Use custom template if specified, otherwise use the default
        template_id_to_use = topic.prompt_id if topic.prompt_id else "article-refinement"
        
        # Try template-based refinement first
        try:
            debug(
                "REFINER",
                "Refining article with template",
                f"Topic: {topic.name}, Template: {template_id_to_use}, Source: {feed_item.url}",
            )
            
            refined_content = template_service.refine_article_with_template(
                template_id=template_id_to_use,
                topic_title=topic.name,
                topic_description=topic.description,
                existing_article=article.content,
                new_context=feed_content,
                new_information=new_information or "",
                enforcing_information=enforcing_information or "",
                contradicting_information=contradicting_information or "",
                llm_config="article_refinement"
            )
            
        except Exception as template_error:
            # If template-based refinement fails, fall back to legacy method
            debug("REFINER", "Template refinement failed, falling back to legacy method", 
                  f"Error: {str(template_error)}")
            
            refined_content = _refine_article_legacy(
                topic, article, feed_content, new_information,
                enforcing_information, contradicting_information
            )

        # Update the article in the database
        refined_article = update_article(
            article_id=article.id, content=refined_content, feed_item=feed_item
        )

        # Update the topic reference and save
        topic.article = refined_article.id

        # Store the article ID in the feed item
        feed_item.article_id = refined_article.id

        # Save the topic with updated feed item
        save_topic(topic)

        info(
            "CURATOR",
            "Article refined",
            f"Topic: {topic.name}, Source: {feed_item.url}",
        )

        # Update state with refined article
        new_state["refined_article"] = refined_article

        return new_state

    except Exception as e:
        return _handle_refinement_error(state, e)


def _refine_article_legacy(
    topic, article, feed_content, new_information, 
    enforcing_information, contradicting_information
) -> str:
    """
    Legacy article refinement using prompt templates.
    
    Args:
        topic: Topic object
        article: Article object
        feed_content: New content from feed
        new_information: New information to integrate
        enforcing_information: Supporting information
        contradicting_information: Contradicting information
        
    Returns:
        Refined article content
        
    Raises:
        Exception: If refinement fails
    """
    from api.db.prompt_db import get_prompt
    from langchain.prompts import PromptTemplate
    from services.llm_service import get_llm
    from utils.rate_limit_utils import retry_with_backoff
    
    # Get the LLM
    llm = get_llm("article_refinement")

    # Get the prompt template from the database
    prompt_data = get_prompt("article-refinement")
    if not prompt_data:
        raise ValueError("Article refinement prompt not found in the database")

    # Create and format the prompt
    prompt = PromptTemplate.from_template(prompt_data.template)

    # Invoke the LLM to refine the article
    debug("REFINER", "Refining article (legacy)", f"Topic: {topic.name}")

    # Use retry decorator for LLM call
    @retry_with_backoff(max_retries=3, base_delay=2.0, max_delay=120.0)
    def _invoke_llm():
        from utils.date_utils import get_current_datetime_context, format_datetime_context_for_prompt
        
        # Get current date/time context
        datetime_context = get_current_datetime_context()
        datetime_info = format_datetime_context_for_prompt(datetime_context)
        
        # Format the prompt with date/time context
        formatted_prompt = prompt.format(
            topic_title=topic.name,
            topic_description=topic.description,
            article=article.content,
            new_context=feed_content,
            new_information=new_information or "",
            enforcing_information=enforcing_information or "",
            contradicting_information=contradicting_information or "",
        )
        
        # Add date/time context to the prompt
        enhanced_prompt = f"{formatted_prompt}\n\n## Current Date/Time Context\n\n{datetime_info}\n\n**Important:** Use this date/time information to properly contextualize any temporal references in the content, especially when determining if news is about past, present, or future events."
        
        return llm.invoke(enhanced_prompt).content

    return _invoke_llm()
