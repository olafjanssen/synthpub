"""
Error classes for the curator chain.
"""
from typing import Any, Optional

class ChainStopError(Exception):
    """
    General exception to stop the chain execution.
    
    This exception can be raised by any step in the chain to stop execution.
    It includes context about why the chain was stopped.
    """
    def __init__(self, message: str, **context):
        self.message = message
        self.context = context
        super().__init__(f"Chain stopped: {message}") 