"""Article generator using LLM."""
from langchain.prompts import PromptTemplate
from .llm_utils import get_llm
from api.db.prompt_db import get_prompt

def generate_article(topic_title: str, topic_description: str) -> str:
    """
    Generate an article based on a topic using the configured LLM.
    
    Args:
        topic_title: Title of the topic to write about
        topic_description: Description and context for the topic to write about
        
    Returns:
        Generated article content as string
    """
    llm = get_llm('article_generation')
    
    # Get the prompt template from the database
    prompt_data = get_prompt('article-generation')
    if not prompt_data:
        raise ValueError("Article generation prompt not found in the database")
    
    prompt = PromptTemplate.from_template(prompt_data.template)
    
    return llm.invoke(prompt.format(
        topic_title=topic_title,
        topic_description=topic_description
    )).content