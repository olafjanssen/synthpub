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
    get_recent_logs
)

def generate_log_messages():
    """Generate a variety of log messages for testing."""
    print("Generating log messages...")
    
    # Generate system logs of different levels
    debug("TEST", "Debug message", "Details only visible in debug mode")
    info("TEST", "Info message", "System running normally")
    warning("TEST", "Warning message", "Resource usage at 85%")
    error("TEST", "Error message", "Connection failed to external API")
    critical("TEST", "Critical message", "Database connection lost")
    
    # Generate logs for different components
    info("TOPIC", "Created", f"Topic {random.randint(1, 100)}")
    time.sleep(0.5)  # Small delay to space out messages
    info("ARTICLE", "Generation complete", "AI Ethics in 2023")
    time.sleep(0.5)
    warning("FEED", "Connection slow", "news.example.com (2.5s)")
    time.sleep(0.5)
    error("PUBLISH", "Failed", "Twitter API rate limit exceeded")
    
    print("Log messages generated.")
    print("Recent logs:")
    for log in get_recent_logs()[-5:]:
        print(f"{log['timestamp'][:19]} | {log['component']} | {log['action']} | {log.get('detail', '')}")

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