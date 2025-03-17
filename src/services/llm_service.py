import os

import yaml
from langchain.chat_models import init_chat_model
from langchain.globals import set_llm_cache
from langchain_core.caches import InMemoryCache
from langchain_core.rate_limiters import InMemoryRateLimiter

set_llm_cache(InMemoryCache())

def load_llm_settings():
    """Load LLM settings from settings.yaml"""
    if os.path.exists("settings.yaml"):
        with open("settings.yaml", 'r') as f:
            settings = yaml.safe_load(f)
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
    
    # Create rate limiter
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=0.75,
    )
    
    # Map providers to their API key environment variables
    provider_api_keys = {
        "openai": "OPENAI_API_KEY",
        "mistralai": "MISTRAL_API_KEY",
    }
        
    # Prepare API key if needed
    api_key = None
    api_key_env = provider_api_keys[provider]
    if api_key_env:
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"{api_key_env} not found in environment variables")
    
    # Initialize the chat model using the generalized method
    return init_chat_model(
        provider=provider,
        model=model_name,
        api_key=api_key,
        max_tokens=max_tokens,
        rate_limiter=rate_limiter,
        temperature=0,
    ) 