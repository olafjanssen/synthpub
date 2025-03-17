"""
Input creator step for the curator workflow.

This module handles loading topic and article data based on the topic_id.
"""

from typing import Any, Callable, Dict

from langgraph.graph import END

from api.db.article_db import get_article
from api.db.topic_db import get_topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from api.models.topic import Topic
from utils.logging import debug, error, warning


def should_skip_news(
    true_node: str, false_node: str
) -> Callable[[Dict[str, Any]], str]:
    """
    Create a routing function that decides if we need to skip the news feed item.

    Args:
        true_node: Node to route to if news feed item should be skipped
        false_node: Node to route to if news feed item should not be skipped
        error_node: Node to route to if there's an error

    Returns:
        A function that takes state and returns the next node identifier
    """

    def _should_skip_news(state: Dict[str, Any]) -> str:
        """Inner function that evaluates the state and returns the next node."""

        topic: Topic = state.get("topic")
        feed_item: FeedItem = state.get("feed_item")

        processed_items = {
            (item.url, item.content_hash): item for item in topic.processed_feeds
        }

        if (feed_item.url, feed_item.content_hash) in processed_items:
            debug(
                "CURATOR", "Skipping processed news feed item", f"URL: {feed_item.url}"
            )
            return true_node

        debug("CURATOR", "News feed item not yet processed.")
        return false_node

    return _should_skip_news


def process(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create input by loading topic and article data from the database.

    Args:
        state: Current workflow state with at least topic_id

    Returns:
        Updated state with topic and existing_article
    """
    debug("CURATOR", "Preparing curator inputs")

    # Create new state starting with current state
    new_state = {**state}

    # Extract the topic_id (this is the only required input)
    topic_id = state.get("topic_id")

    # Load the topic from the database
    topic: Topic = get_topic(topic_id)

    # Get the current article if one exists
    article: Article = None
    if topic.article:
        article = get_article(topic.article)

    # Update the state with loaded data
    new_state["topic"] = topic
    new_state["existing_article"] = article

    return new_state
