"""
Curator workflow steps package.

This package contains modules for each step in the curator workflow.
"""
# Import the process functions from each step module
from .input_creator import process as process_input, should_skip_news
from .news_relevance import process as news_relevance, is_relevant
from .article_refiner import process as refine_article
from .article_generator import process as generate_article, should_generate

# For compatibility with old code
from .input_creator import process as InputCreatorStep
from .news_relevance import process as RelevanceFilterStep
from .article_refiner import process as ArticleRefinerStep
from .article_generator import process as ArticleGeneratorStep

__all__ = [
    # New function-based API
    'process_input',
    'news_relevance',
    'refine_article',
    'generate_article',
    
    # Conditional routing functions
    'should_generate',
    'is_relevant',
    'should_skip_news',
    
    # Legacy class names for backward compatibility
    'InputCreatorStep', 
    'RelevanceFilterStep', 
    'ArticleRefinerStep', 
    'ArticleGeneratorStep',
] 