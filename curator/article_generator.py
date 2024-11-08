"""
Article generator using Ollama LLM.
"""
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from .config import config

def generate_article(topic: str) -> str:
    """
    Generate an article about a given topic using Ollama.
    
    Args:
        topic: The topic to write about
        
    Returns:
        str: Generated article text
    """
    model_name = config['llm']['article_generation']['model_name']
    llm = OllamaLLM(model=model_name)
    
    prompt = PromptTemplate.from_template(
        "Write a concise, informative article about {topic}. "
        "The article should be 2-3 paragraphs long and focus on the most important aspects. "
        "Use a neutral, factual tone."
    )
    
    return llm.invoke(prompt.format(topic=topic)) 