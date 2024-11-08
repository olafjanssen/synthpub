"""
Article refiner module for updating existing articles with new context.
"""
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from .config import config

def refine_article(article: str, new_context: str) -> str:
    """
    Refine an existing article with new context.
    
    Args:
        article: Original article text
        new_context: New information to incorporate
        
    Returns:
        str: Refined article text
    """
    model_name = config['llm']['article_refinement']['model_name']
    llm = OllamaLLM(model=model_name)
    
    prompt = PromptTemplate.from_template(
        "Here is an existing article:\n\n{article}\n\n"
        "Given this new context:\n{new_context}\n\n"
        "Please create an updated version of the article that incorporates "
        "the new information while maintaining the same concise style. "
        "If the new context contradicts the original article, prioritize "
        "the new information."
    )
    
    return llm.invoke(prompt.format(
        article=article,
        new_context=new_context
    )) 