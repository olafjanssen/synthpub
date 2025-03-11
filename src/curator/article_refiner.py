"""
Article refiner module for updating existing articles with new context.
"""
from langchain.prompts import PromptTemplate
from .llm_utils import get_llm
from api.db.prompt_db import get_prompt

def refine_article(topic_title: str, topic_description: str, article: str, new_context: str) -> str:
    """
    Refine an existing article with new context.
    
    Args:
        topic_title: Title of the topic to write about
        topic_description: Description and context for the topic to write about
        article: Original article text
        new_context: New information to incorporate
        
    Returns:
        str: Refined article text
    """
    llm = get_llm('article_refinement')
    
    # Get the prompt template from the database
    prompt_data = get_prompt('article-refinement')
    if not prompt_data:
        raise ValueError("Article refinement prompt not found in the database")
    
    prompt = PromptTemplate.from_template(prompt_data.template)
    
    return llm.invoke(prompt.format(
        topic_title=topic_title,
        topic_description=topic_description,
        article=article,
        new_context=new_context
    )).content 