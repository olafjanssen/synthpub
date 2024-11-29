"""
Article refiner module for updating existing articles with new context.
"""
from langchain.prompts import PromptTemplate
from .llm_utils import get_llm

def refine_article(article: str, new_context: str) -> str:
    """
    Refine an existing article with new context.
    
    Args:
        article: Original article text
        new_context: New information to incorporate
        
    Returns:
        str: Refined article text
    """
    llm = get_llm('article_refinement')
    
    prompt = PromptTemplate.from_template(
        "Here is an existing article:\n\n{article}\n\n"
        "Given this new context:\n{new_context}\n\n"
        "Please create an updated version of the article that incorporates "
        "the new information while maintaining the same concise style. Try to keep as much as the original article as possible."
        "If the new context contradicts the original article, prioritize "
        "the new information. Keep it within 300-500 words."
    )
    
    return llm.invoke(prompt.format(
        article=article,
        new_context=new_context
    )).content 