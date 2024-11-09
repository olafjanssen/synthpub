"""Article generator using Ollama LLM."""
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from .config import config

def generate_article(topic_description: str) -> str:
    """
    Generate an article based on a topic using local Ollama LLM.
    
    Args:
        topic_description: Description of the topic to write about
        
    Returns:
        Generated article content as string
    """
    model_name = config['llm']['article_generation']['model_name']
    llm = OllamaLLM(model=model_name, num_predict=config['llm']['article_generation']['max_tokens'])
    
    prompt = PromptTemplate.from_template(
        """You are an expert content writer. Write a clear and engaging article 
        about the following topic. The article should start with a title and be
        informative but concise (around 300-500 words).
        
        Topic: {topic_description}"""
    )
    
    content = llm.invoke(prompt.format(topic_description=topic_description))
    
    return content.strip()