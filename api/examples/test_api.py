"""
Example script to test the SynthPub API endpoints.
"""
import requests
import json
from typing import Dict, Any

API_URL = "http://localhost:8000"

def print_response(response: requests.Response):
    """Helper function to print formatted API responses."""
    print(f"\nStatus Code: {response.status_code}")
    try:
        print("Response:", json.dumps(response.json(), indent=2))
    except:
        print("Response:", response.text)

def test_create_topic():
    """Test creating a new topic."""
    print("\n=== Testing Topic Creation ===")
    
    # Test data
    topic_data = {
        "name": "python_basics",
        "description": "Introduction to Python programming language"
    }
    
    # Create topic
    response = requests.post(f"{API_URL}/topics/", json=topic_data)
    print_response(response)
    
    # Try creating same topic again (should fail)
    print("\n--- Testing duplicate topic creation ---")
    response = requests.post(f"{API_URL}/topics/", json=topic_data)
    print_response(response)

def test_list_topics():
    """Test listing all topics."""
    print("\n=== Testing Topics Listing ===")
    
    response = requests.get(f"{API_URL}/topics/")
    print_response(response)

def main():
    """Run all API tests."""
    print("Running API tests...")
    try:
        test_create_topic()
        test_list_topics()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Make sure the API server is running on http://localhost:8000") 


if __name__ == "__main__":
    main() 