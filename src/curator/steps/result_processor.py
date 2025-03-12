"""
Result processor step for the curator chain.
"""
from langchain.schema.runnable import Runnable
from typing import Dict, Any, Union

from api.models.topic import Topic
from utils.logging import debug

class ResultProcessorStep(Runnable):
    """Runnable step that processes the chain results into a boolean value."""
    
    def invoke(self, inputs: Dict[str, Any], config=None) -> Dict[str, Any]:
        """
        Process chain results into a boolean value.
        
        Args:
            inputs: Dictionary with chain results including is_relevant and success flags
            config: Optional configuration for the runnable
            
        Returns:
            Dictionary with original inputs and result flag added
        """
        topic: Topic = inputs["topic"]
        result = inputs.get("is_relevant", False) and not inputs.get("should_stop", False)
        
        debug("CURATOR", f"Chain result: {result}", f"Topic: {topic.name}")
        return {
            **inputs,
            "result": result
        }