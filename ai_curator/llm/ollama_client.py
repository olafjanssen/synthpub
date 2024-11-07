from typing import Dict, List, Optional
import httpx
import json
import numpy as np
from .base import BaseLLM

class OllamaClient(BaseLLM):
    """Client for interacting with Ollama API."""
    
    def __init__(
        self, 
        model_name: str = "smollm:135m", 
        base_url: str = "http://localhost:11434",
        config: Optional[Dict] = None
    ):
        super().__init__(model_name, config)
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=60.0)
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama."""
        try:
            response = await self.client.post(
                "/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "timeout": 60.0,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json()["response"]
            
        except Exception as e:
            self.logger.error(f"Ollama generation error: {str(e)}")
            raise
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using Ollama."""
        try:
            response = await self.client.post(
                "/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text
                }
            )
            response.raise_for_status()
            return response.json()["embedding"]
            
        except Exception as e:
            self.logger.error(f"Ollama embedding error: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False 