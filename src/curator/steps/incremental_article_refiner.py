"""
Incremental article refiner step for the curator workflow.

This module refines existing articles with new relevant content using a step-by-step approach
that makes minimal, controlled changes to avoid disrupting the article's flow.
"""

from typing import Any, Dict, List

from api.db.article_db import update_article
from api.db.topic_db import save_topic
from utils.logging import debug, error, info


def _handle_refinement_error(state: Dict[str, Any], e: Exception) -> Dict[str, Any]:
    """Handle errors in the refinement process."""
    error_message = str(e)
    error("CURATOR", "Failed to refine article incrementally", error_message)
    new_state = {**state}
    new_state["has_error"] = True
    new_state["error_message"] = f"Failed to refine article incrementally: {error_message}"
    new_state["error_step"] = "incremental_article_refiner"
    return new_state


def process(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refine an existing article with new relevant content using incremental steps.

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
        # Use template-based incremental refinement
        from curator.template_service import template_service
        
        # Determine which template to use for refinement
        template_id_to_use = topic.prompt_id if topic.prompt_id else "incremental-refinement"
        
        debug("REFINER", "Using incremental template refinement", f"Topic: {topic.name}, Template: {template_id_to_use}")
        
        # Use template service for structured incremental refinement
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
            "Article refined incrementally",
            f"Topic: {topic.name}, Source: {feed_item.url}",
        )

        # Update state with refined article
        new_state["refined_article"] = refined_article

        return new_state

    except Exception as e:
        return _handle_refinement_error(state, e)


# The incremental refiner now uses the template service for structured refinement
# All the step-by-step functions have been removed in favor of the unified template approach
