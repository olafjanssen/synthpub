from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config
    
    @abstractmethod
    async def process(self, data: Dict) -> Dict:
        """Abstract method to process data."""
        pass
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data before processing."""
        return True
    
    def format_output(self, result: Any) -> Dict:
        """Format the processing results."""
        return {'status': 'success', 'data': result} 