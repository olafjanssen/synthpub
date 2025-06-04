# curator/__init__.py (or curator_steps.py)
from api.db.version_graph import ArticleVersionGraph

# Create a single global instance of the version graph
version_graph = ArticleVersionGraph()

# Import and re-export your step modules/functions as usual

from .article_generator import process as generate_article
from .article_generator import should_generate
from .article_refiner import process as refine_article
from .input_creator import process as process_input
from .input_creator import should_skip_news
from .news_relevance import is_relevant
from .news_relevance import process as news_relevance
from .substance_extractor import process as extract_substance

__all__ = [
    "process_input",
    "news_relevance",
    "refine_article",
    "generate_article",
    "extract_substance",
    "should_generate",
    "is_relevant",
    "should_skip_news",
    "version_graph",  # Expose the graph instance if desired
]
