"""
LangGraph-based topic curator workflow.

This module implements a LangGraph workflow that replaces the previous LCEL chain
for topic curation. It provides better state management, error handling, and visualization.
"""
from typing import Dict, Any, Optional, TypedDict, Union, List, Callable
from langgraph.graph import StateGraph, START, END 

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from utils.logging import debug, info, warning, error

# Import the step functions directly
from curator.steps import process_input, generate_article, news_relevance, refine_article, should_generate, is_relevant, should_skip_news, extract_substance

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
    
    # Extracted substance
    new_information: str
    enforcing_information: str
    contradicting_information: str
    
    # Status flags
    has_error: bool
    error_message: str
    error_step: str

# Identity function for passthrough nodes
def identity(state: Dict[str, Any]) -> Dict[str, Any]:
    """Identity function that returns the state unchanged."""
    return state

# Create the graph
def create_curator_graph() -> Callable:
    """Create and compile the LangGraph curator workflow."""
    # Initialize the graph with our state schema
    graph = StateGraph(CuratorState)
    
    # Add nodes for processing steps
    graph.add_node("prepare_input", process_input)
    graph.add_node("generate_article", generate_article)
    graph.add_node("prepare_news_item", identity)
    graph.add_node("news_relevance", news_relevance)
    graph.add_node("extract_substance", extract_substance)
    graph.add_node("refine_article", refine_article)
        
    # Add edges with explicit routing targets using function factories
    graph.add_conditional_edges("prepare_input", should_generate("no_article", "existing_article"), 
                                path_map={"no_article":"generate_article", "existing_article":"prepare_news_item"})
    graph.add_edge("generate_article","prepare_news_item")
    graph.add_conditional_edges("prepare_news_item", should_skip_news("already_processed", "new news"), 
                                path_map={"new news":"news_relevance", "already_processed": END})    
    graph.add_conditional_edges("news_relevance", is_relevant("relevant", "not_relevant"), 
                                path_map={"relevant":"extract_substance", "not_relevant": END})
    graph.add_edge("extract_substance", "refine_article")
    graph.add_edge("refine_article", END)
    # Set entry point
    graph.set_entry_point("prepare_input")
    
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
    }
    
    # Execute the graph
    try:
        result = graph.invoke(initial_state)
        info("CURATOR", "Graph execution completed", f"Topic: {topic_id}")
        return result
    except Exception as e:
        error("CURATOR", "Graph execution failed", str(e))
        return {
            "topic_id": topic_id,
            "has_error": True,
            "error_message": str(e),
            "error_step": "graph_execution"
        }

