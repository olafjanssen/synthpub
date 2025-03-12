"""
Result processor step for the curator chain.
"""
from langchain.schema.runnable import Runnable
from typing import Dict, Any, Union

from utils.logging import debug

class ResultProcessorStep(Runnable):
    """Runnable step that processes the chain results into a boolean value."""
    
    def invoke(self, inputs: Dict[str, Any], config=None) -> bool:
        """
        Process chain results into a boolean value.
        
        Args:
            inputs: Dictionary with chain results including is_relevant and success flags
            config: Optional configuration for the runnable
            
        Returns:
            Boolean indicating if the content was relevant and successfully processed
        """
        topic_name = inputs["topic"].name if "topic" in inputs else "Unknown"
        result = inputs["is_relevant"] and inputs.get("success", False)
        
        debug("CURATOR", f"Chain result: {result}", f"Topic: {topic_name}")
        return result 