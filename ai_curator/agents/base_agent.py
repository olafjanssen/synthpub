from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseAgent(ABC):
    """Base class for all AI agents in the system."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    @abstractmethod
    async def process(self, data: Any) -> Dict:
        """Process the input data and return results."""
        pass
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data before processing."""
        return True
    
    def format_output(self, result: Any) -> Dict:
        """Format the processing results."""
        return {'status': 'success', 'data': result} 