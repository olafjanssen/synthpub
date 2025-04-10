"""
Article generator step for the curator workflow.

This module handles generating new articles for topics that don't have one yet.
"""

from datetime import datetime
from typing import Any, Callable, Dict

from langchain.prompts import PromptTemplate

from api.db.article_db import create_article
from api.db.prompt_db import get_prompt
from api.db.topic_db import save_topic
from api.models.article import Article
from api.models.topic import Topic
# Import the global version graph instance from the curator package
from curator.steps import version_graph
from services.llm_service import get_llm
from utils.logging import debug, error, info


def should_generate(true_node: str, false_node: str) -> Callable[[Dict[str, Any]], str]:
    """
    Create a routing function that decides if we need to generate a new article.

    Args:
        true_node: Node to route to if article needs to be generated
        false_node: Node to route to if article exists

    Returns:
        A function that takes state and returns the next node identifier.
    """

    def _should_generate_router(state: Dict[str, Any]) -> str:
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
        state: Current workflow state with topic and existing_article.

    Returns:
        Updated state with generated_article if one was created.
    """
    new_state = {**state}
    topic = state.get("topic")
    feed_item = state.get("feed_item")

    try:
        # Generate the article using the helper function
        new_article = generate_article(topic)

        # Update state with the new article
        new_state["generated_article"] = new_article
        new_state["existing_article"] = new_article

        # If there is a feed item, assign the article ID and update the topic
        if feed_item:
            feed_item.article_id = new_article.id
            save_topic(topic)

        # Add a version node to the global version graph
        # For the first version, we can use a simple scheme like appending "-v1"
        version_id = f"{new_article.id}-v1"
        version_graph.add_version(
            article_id=new_article.id,
            version_id=version_id,
            content=new_article.content,
            timestamp=datetime.utcnow(),
            metadata={"reason": "initial creation"},
        )

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
        topic: The topic for which the article is to be generated.

    Returns:
        The generated article.

    Raises:
        Exception: If article generation fails.
    """
    topic_title = topic.name
    topic_description = topic.description

    # Get the LLM service for article generation
    llm = get_llm("article_generation")

    # Retrieve the prompt template from the database
    # Use custom prompt if specified, otherwise use the default
    prompt_id_to_use = topic.prompt_id if topic.prompt_id else "starter-general-article"
    prompt_data = get_prompt(prompt_id_to_use)
    if not prompt_data:
        if topic.prompt_id:
            # Custom prompt not found, log a warning and fall back to default
            info("GENERATOR", "Custom prompt not found", f"Falling back to default prompt. Custom prompt ID: {topic.prompt_id}")
            prompt_data = get_prompt("starter-general-article")
            if not prompt_data:
                raise ValueError("Article generation prompt not found in the database")
        else:
            raise ValueError("Article generation prompt not found in the database")

    info("GENERATOR", "Using prompt", f"Prompt: {prompt_data.template}")

    # Create and format the prompt
    prompt = PromptTemplate.from_template(prompt_data.template)

    # Invoke the LLM to generate content
    info("GENERATOR", "Generating article", f"Topic: {topic_title}")
    content = llm.invoke(
        prompt.format(topic_title=topic_title, topic_description=topic_description)
    ).content

    # Create the article using the database function
    new_article = create_article(title=topic_title, topic_id=topic.id, content=content)

    # Update the topic with the new article ID and save changes
    topic.article = new_article.id
    save_topic(topic)

    info("GENERATOR", "Article generated", f"Topic: {topic_title}")
    return new_article
