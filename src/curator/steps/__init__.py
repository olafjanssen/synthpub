"""
Curator workflow steps package.

This package contains modules for each step in the curator workflow.
"""

from .article_generator import process as generate_article
from .article_generator import should_generate
from .article_refiner import process as refine_article

# Import the process functions from each step module
from .input_creator import process as process_input
from .input_creator import should_skip_news
from .news_relevance import is_relevant
from .news_relevance import process as news_relevance
from .substance_extractor import process as extract_substance

__all__ = [
    # New function-based API
    "process_input",
    "news_relevance",
    "refine_article",
    "generate_article",
    "extract_substance",
    # Conditional routing functions
    "should_generate",
    "is_relevant",
    "should_skip_news",
]
