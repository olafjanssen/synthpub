"""
Article refiner module for updating existing articles with new context.
"""
from langchain.prompts import PromptTemplate
from .llm_utils import get_llm

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
    
    prompt = PromptTemplate.from_template(
        """
        You are an expert content writer for a Wikipedia-like article.

        Topic title: {topic_title}
        Topic description: {topic_description}

        Here is an existing article for this topic:

        {article}

        Given this new context:
        {new_context}

Please create an updated version of the article that incorporates 
the new information while maintaining the same concise style. Try to keep as much as the original article as possible.
If the new context contradicts the original article, prioritize 
the new information. Keep it within 300-500 words."""
    )
    
    return llm.invoke(prompt.format(
        topic_title=topic_title,
        topic_description=topic_description,
        article=article,
        new_context=new_context
    )).content 