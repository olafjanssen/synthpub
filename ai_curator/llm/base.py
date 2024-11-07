from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

class BaseLLM(ABC):
    """Base class for LLM interactions."""
    
    def __init__(self, model_name: str, config: Optional[Dict] = None):
        self.model_name = model_name
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM is available."""
        pass 