"""Base interface for publishers."""
from typing import Protocol
from typing_extensions import runtime_checkable
from api.signals import convert_requested
from api.models import Topic
from utils.logging import debug, error

@runtime_checkable
class Converter(Protocol):
    """Protocol for converters."""
    
    @staticmethod
    def can_handle(type: str) -> bool:
        """Check if this converter can handle the given type."""
        ...
        
    @staticmethod
    def convert_representation(type: str, topic: Topic) -> bool:
        """
        Publish content to the given URL.
        
        Args:
            type: The type to convert to
            topic: The topic to convert
            
        Returns:
            bool: True if conversion succeeded
        """
        ... 

    @classmethod
    def handle_convert_requested(cls, sender, type: str):
        """Handle conversion request signal."""
        debug("CONVERT", "Checking handler", f"Type: {type}, Handler: {cls.__name__}")
        if cls.can_handle(type):
            debug("CONVERT", "Using handler", f"Type: {type}, Handler: {cls.__name__}")
            try:
                cls.convert_representation(type, sender)
            except Exception as e:
                error("CONVERT", "Failed", f"Type: {type}, Error: {str(e)}")
        else:
            debug("CONVERT", "No suitable handler", f"Type: {type}, Handler: {cls.__name__}")
            
    @classmethod
    def connect_signals(cls):
        """Connect to conversion signals."""
        convert_requested.connect(cls.handle_convert_requested) 