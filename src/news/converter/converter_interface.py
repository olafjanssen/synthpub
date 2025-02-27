"""Base interface for publishers."""
from typing import Dict, Protocol
from typing_extensions import runtime_checkable
from api.signals import topic_converted, convert_requested
from api.models import Topic

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
        """Handle feed update request signal."""
        print(f"Trying handling convert request for {type} as {cls.__name__}")
        if cls.can_handle(type):
            print(f"Can handle convert request for {type} as {cls.__name__}")
            try:
                cls.convert_content(type, sender)
                topic_converted.send(sender, type=type)
            except Exception as e:
                print(f"Error converting {type}: {str(e)}")
        else:
            print(f"Cannot handle convert request for {type} as {cls.__name__}")
            
    @classmethod
    def connect_signals(cls):
        """Connect to feed update signals."""
        convert_requested.connect(cls.handle_convert_requested) 