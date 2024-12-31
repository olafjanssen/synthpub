"""Article generator using LLM."""
from langchain.prompts import PromptTemplate
from .llm_utils import get_llm

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
    
    prompt = PromptTemplate.from_template(
        """You are an expert content writer for a Wikipedia-like article. Create a minimal Markdown header structure for an article about the following topic.
        Choose a clear and concise title and write a short introduction solely based on the topic title and description.
        
        Topic title: {topic_title}
        Topic description: {topic_description}"""
    )

    content = llm.invoke(prompt.format(topic_title=topic_title, topic_description=topic_description)).content
    
    return content.strip()