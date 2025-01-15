from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from .config import config
import os

def get_llm(task: str):
    """
    Initialize the LLM based on the task and configuration.

    Args:
        task: The task for which the LLM is needed ('article_generation' or 'article_refinement')

    Returns:
        An instance of the LLM
    """
    provider = config['llm'][task]['provider']
    model_name = config['llm'][task]['model_name']
    max_tokens = config['llm'][task]['max_tokens']
    
    if provider == "ollama":
        return ChatOllama(model=model_name, num_predict=max_tokens)
    elif provider == "openai":
        # Get API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize OpenAI using langchain
        return ChatOpenAI(
            model_name=model_name,
            max_tokens=max_tokens,
            openai_api_key=api_key
        )
    else:
        raise ValueError("Unsupported LLM provider specified in the configuration.")