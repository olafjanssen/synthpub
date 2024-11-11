"""Article generator using LLM."""
from langchain.prompts import PromptTemplate
from .llm_utils import get_llm

def generate_article(topic_description: str) -> str:
    """
    Generate an article based on a topic using the configured LLM.
    
    Args:
        topic_description: Description of the topic to write about
        
    Returns:
        Generated article content as string
    """
    llm = get_llm('article_generation')
    
    prompt = PromptTemplate.from_template(
        """You are an expert content writer. Write a clear and engaging article 
        about the following topic in the language of the given description. The article should start with a title and be
        informative but concise (around 300-500 words).
        
        Topic: {topic_description}"""
    )
    
    content = llm.invoke(prompt.format(topic_description=topic_description)).content
    
    return content.strip()