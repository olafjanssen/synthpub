"""
Example script to test the SynthPub API endpoints.
"""
import requests
import json
import shutil
from pathlib import Path

API_URL = "http://localhost:8000"
DB_PATH = Path("db")

def clean_database():
    """Remove all files from the db folder."""
    print("\n=== Cleaning Database ===")
    
    if DB_PATH.exists():
        shutil.rmtree(DB_PATH)
        print("Database cleaned")
    
    # Recreate empty db folder structure
    (DB_PATH / "articles").mkdir(parents=True, exist_ok=True)
    (DB_PATH / "topics").mkdir(parents=True, exist_ok=True)
    print("Database structure recreated")

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
    
    topic_data = {
        "name": "MDA Framework",
        "description": "Concise overview of the Mechanics-Dynamics-Aesthetics (MDA) framework in Game Design.",
        "feed_urls": ["https://en.wikipedia.org/wiki/MDA_framework"]
    }


    # Create topic
    response = requests.post(f"{API_URL}/topics/", json=topic_data)
    print_response(response)
    
    # More safely get topic ID
    if response.status_code == 200:
        response_data = response.json()
        topic_id = response_data.get("id")
        if not topic_id:
            print("Warning: No topic ID returned in response")
            return None
        return topic_id
    else:
        print(f"Error creating topic: {response.status_code}")
        return None

def test_get_topic(topic_id: str):
    """Test getting a specific topic."""
    print("\n=== Testing Get Topic ===")
    
    response = requests.get(f"{API_URL}/topics/{topic_id}")
    print_response(response)
    
    print("\n--- Testing get non-existent topic ---")
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    response = requests.get(f"{API_URL}/topics/{fake_id}")
    print_response(response)

def test_list_topics():
    """Test listing all topics."""
    print("\n=== Testing Topics Listing ===")
    
    response = requests.get(f"{API_URL}/topics/")
    print_response(response)

def test_update_feeds(topic_id: str):
    """Test updating feed URLs for a topic."""
    print("\n=== Testing Update Feed URLs ===")

def test_update_topic(topic_id: str):
    """Test updating a topic's article based on feed content."""
    print("\n=== Testing Topic Update ===")
    
    # Test updating existing topic
    response = requests.post(f"{API_URL}/topics/{topic_id}/update")
    print_response(response)
    
    print("\n--- Testing update non-existent topic ---")
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    response = requests.post(f"{API_URL}/topics/{fake_id}/update")
    print_response(response)

def main():
    """Run all API tests."""
    try:
        # Clean database before running tests
        clean_database()
        
        topic_id = test_create_topic()
        if topic_id:
            test_get_topic(topic_id)
            test_update_feeds(topic_id)
            test_update_topic(topic_id)
        test_list_topics()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API.")
        print("Make sure the API server is running on http://localhost:8000")

if __name__ == "__main__":
    main() 