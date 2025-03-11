"""
Article refiner module for updating existing articles with new context.
"""
from langchain.prompts import PromptTemplate
from .llm_utils import get_llm
from utils.logging import debug
from api.db.prompt_db import get_prompt

def filter_relevance(topic_title: str, topic_description: str, article: str, new_context: str) -> bool:
    """
    Determine if new context is relevant to the existing article.
    
    Args:
        topic_title: Title of the topic to write about
        topic_description: Description and context for the topic to write about
        article: Current article text
        new_context: New text to evaluate
        
    Returns:
        bool: True if the new context is relevant
    """
    # Get the prompt template from the database
    prompt_data = get_prompt('article-relevance-filter')
    if not prompt_data:
        raise ValueError("Article relevance filter prompt not found in the database")
    
    prompt = PromptTemplate.from_template(prompt_data.template)
    
    llm = get_llm('article_refinement')
    response = llm.invoke(prompt.format(
        topic_title=topic_title,
        topic_description=topic_description,
        article=article,
        new_context=new_context
    )).content
    debug("FILTER", "Response", response)
    return response.strip().upper().startswith('YES')
