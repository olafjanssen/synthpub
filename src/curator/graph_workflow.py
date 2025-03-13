"""
LangGraph-based topic curator workflow.

This module implements a LangGraph workflow that replaces the previous LCEL chain
for topic curation. It provides better state management, error handling, and visualization.
"""
from typing import Dict, Any, Optional, TypedDict, Union, List, Callable
from langgraph.graph import StateGraph, END

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from utils.logging import debug, info, warning, error

# Import the step functions directly
from curator.steps import process_input, generate_article, news_relevance, refine_article, should_generate, is_relevant

# Define the state schema
class CuratorState(TypedDict, total=False):
    """State definition for the curator workflow."""
    # Input parameters
    topic_id: str
    feed_content: Optional[str]
    feed_item: Optional[FeedItem]
    
    # Loaded entities
    topic: Optional[Topic]
    existing_article: Optional[Article]
    
    # Generated entities
    refined_article: Optional[Article]
    generated_article: Optional[Article]
    
    # Status flags
    is_relevant: bool
    has_error: bool
    error_message: str
    error_step: str
    current_step: str

# Create the graph
def create_curator_graph() -> Callable:
    """Create and compile the LangGraph curator workflow."""
    # Initialize the graph with our state schema
    graph = StateGraph(CuratorState)
    
    # Add nodes for processing steps
    graph.add_node("create_input", process_input)
    graph.add_node("generate_article", generate_article)
    graph.add_node("news_relevance", news_relevance)
    graph.add_node("refine_article", refine_article)
    
    # Add terminal node
    graph.add_node("end", lambda x: {"state": x})
    
    # Add edges with explicit routing targets using function factories
    graph.add_conditional_edges("create_input", should_generate("generate_article", "news_relevance", "end"))
    graph.add_edge("generate_article", "news_relevance")
    graph.add_conditional_edges("news_relevance", is_relevant("refine_article", "end", "end"))
    graph.add_edge("refine_article", "end")
    
    # Set entry point
    graph.set_entry_point("create_input")
    
    # Compile the graph
    return graph.compile()

def process_feed_item(
    topic_id: str,
    feed_content: Optional[str] = None,
    feed_item: Optional[FeedItem] = None
) -> Dict[str, Any]:
    """
    Process a feed item through the curator graph.
    
    Args:
        topic_id: The ID of the topic
        feed_content: The content from the feed (optional)
        feed_item: The feed item being processed (optional)
        
    Returns:
        The final state after processing
    """
    # Create the graph
    graph = create_curator_graph()
    
    # Initial state
    initial_state = {
        "topic_id": topic_id,
        "feed_content": feed_content,
        "feed_item": feed_item,
        "has_error": False,
        "is_relevant": False,
        "current_step": "start"
    }
    
    # Execute the graph
    try:
        result = graph.invoke(initial_state)        
        return result
    except Exception as e:
        error("CURATOR", "Graph execution failed", str(e))
        return {
            "topic_id": topic_id,
            "has_error": True,
            "error_message": str(e),
            "error_step": "graph_execution"
        }

