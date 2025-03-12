"""LCEL-based curator chain processor.

This module implements a curator chain using LangChain Expression Language (LCEL).
Each step in the chain is implemented as a separate Runnable class with its processing
logic contained within the class, providing a clean, modular architecture.
"""
from typing import Dict, Any

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem

from curator.steps import InputCreatorStep, RelevanceFilterStep, ArticleRefinerStep, ResultProcessorStep

def process_curator_chain(
    topic: Topic,
    current_article: Article,
    feed_content: str,
    feed_item: FeedItem
) -> bool:
    """
    Process the curator chain using LCEL.
    
    Args:
        topic: The topic being processed
        current_article: The current article
        feed_content: The content from the feed
        feed_item: The feed item being processed
        
    Returns:
        bool: Whether the content passed all curation steps and is relevant
    """
    # Initialize step components
    input_creator = InputCreatorStep()
    relevance_filter = RelevanceFilterStep()
    article_refiner = ArticleRefinerStep()
    result_processor = ResultProcessorStep()
    
    # Create the LCEL chain
    chain = (
        input_creator 
        | relevance_filter 
        | article_refiner 
        | result_processor
    )
    
    # Execute the chain
    result = chain.invoke(
        {
            "topic": topic,
            "current_article": current_article,
            "feed_content": feed_content,
            "feed_item": feed_item
        }
    )
    
    return result 