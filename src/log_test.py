"""
Test script to generate log messages and verify WebSocket functionality.
Run this to generate log messages while the main application is running.
"""
import os
import time
import random

# Import logging functions
from utils.logging import (
    debug, info, warning, error, critical, 
    user_info, user_warning, user_error,
    get_recent_logs, get_user_logs
)

def generate_log_messages():
    """Generate a variety of log messages for testing."""
    print("Generating log messages...")
    
    # Generate system logs
    debug("This is a debug message")
    info("This is an info message")
    warning("This is a warning message")
    error("This is an error message")
    critical("This is a critical message")
    
    # Generate user-facing logs (these should appear in the web interface)
    user_info("User info message: Application is running normally")
    time.sleep(1)  # Small delay to space out messages
    user_warning("User warning message: Resource usage is high")
    time.sleep(1)
    user_error("User error message: Could not connect to external service")
    
    print("Log messages generated.")
    print("Recent user logs:")
    for log in get_user_logs()[-3:]:
        print(f"{log['timestamp'][:19]} | {log['level']} | {log['message']}")

if __name__ == "__main__":
    print("=== Log Message Testing Tool ===")
    print("This script generates test log messages to verify WebSocket functionality.")
    print("Make sure the application is running in another terminal.")
    print()
    
    while True:
        generate_log_messages()
        
        print("\nOptions:")
        print("1. Generate more log messages")
        print("2. Exit")
        
        choice = input("Enter your choice (1/2): ")
        if choice == '2':
            break
        
        # Add a random delay between 1-3 seconds
        time.sleep(random.uniform(1, 3)) 