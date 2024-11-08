"""Article generator using Ollama LLM."""
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from .config import config
from typing import Tuple

def generate_article(topic_description: str) -> Tuple[str, str]:
    """
    Generate an article based on a topic using local Ollama LLM.
    
    Args:
        topic_description: Description of the topic to write about
        
    Returns:
        Tuple of (title, content)
    """
    model_name = config['llm']['article_generation']['model_name']
    llm = OllamaLLM(model=model_name)
    
    prompt = PromptTemplate.from_template(
        """You are an expert content writer. Write a clear and engaging article 
        about the following topic. First provide a title, then the article content.
        The article should be informative but concise (around 300-500 words).
        
        Topic: {topic_description}
        
        Title:
        Article:"""
    )
    
    response = llm.invoke(prompt.format(topic_description=topic_description))
    
    # Extract title and content
    lines = response.strip().split("\n")
    title = lines[0].strip()
    content = "\n".join(lines[1:]).strip()
    
    return title, content