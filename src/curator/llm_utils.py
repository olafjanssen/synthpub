from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
import os
import tomli
import time

def load_llm_settings():
    """Load LLM settings from settings.toml"""
    if os.path.exists("settings.toml"):
        with open("settings.toml", 'rb') as f:
            settings = tomli.load(f)
            return settings.get("llm", {})
    return {}

def get_llm(task: str):
    """
    Initialize the LLM based on the task and configuration.

    Args:
        task: The task for which the LLM is needed ('article_generation' or 'article_refinement')

    Returns:
        An instance of the LLM
    """
    settings = load_llm_settings()
    task_settings = settings.get(task, {})
    
    provider = task_settings.get("provider", "openai")
    model_name = task_settings.get("model_name", "gpt-4")
    max_tokens = task_settings.get("max_tokens", 800)
    
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
    elif provider == "mistral":
        # Get API key from environment variable
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        
        # Mistral API is rate limited, instead of using the Langchain fallback, we just wait for 2 seconds
        time.sleep(2) 
        
        # Initialize Mistral using langchain
        return ChatMistralAI(
            model_name=model_name,
            max_tokens=max_tokens,
            mistral_api_key=api_key
        )
    else:
        raise ValueError("Unsupported LLM provider specified in the configuration.")