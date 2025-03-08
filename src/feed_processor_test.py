"""
Simple script to test that the logging system is working properly 
with the updated component-action-detail format.
"""
from utils.logging import debug, info, warning, error

def test_logging():
    """Test all logging levels with the new format."""
    print("Testing logging...")
    
    # Test debug level
    debug("TEST", "Debug test", "This is a debug message")
    
    # Test info level
    info("TEST", "Info test", "This is an info message")
    
    # Test warning level
    warning("TEST", "Warning test", "This is a warning message")
    
    # Test error level
    error("TEST", "Error test", "This is an error message")
    
    print("Logging test complete!")

if __name__ == "__main__":
    test_logging() 