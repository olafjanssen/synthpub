import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

import requests
from ext_sources.html_extractor import extract_html_content

API_URL = "http://localhost:5000/api"

def check_and_delete_topic(topic_name: str):
    """Check if a topic exists and delete it if it does."""
    response = requests.get(f"{API_URL}/topics/")
    response.raise_for_status()
    topics = response.json()
    
    for topic in topics:
        if topic['name'] == topic_name:
            delete_response = requests.delete(f"{API_URL}/topics/{topic['id']}")
            delete_response.raise_for_status()
            print(f"Deleted existing topic: {topic_name}")
            return

def create_topic(topic_name: str):
    response = requests.post(f"{API_URL}/topics/", json={'name': topic_name, 'description': 'Description of AI Innovations'})
    response.raise_for_status()
    return response.json()

def create_initial_article(topic_id: int, topic_name: str):
    response = requests.post(
        f"{API_URL}/articles/create-initial",
        json={'topic_id': topic_id, 'topic': topic_name}
    )
    response.raise_for_status()
    return response.json()

def update_article_with_curator(article_id: int, content: str, topic: str):
    response = requests.post(
        f"{API_URL}/curator/update-article/{article_id}",
        json={'content': content, 'topic': topic}
    )
    response.raise_for_status()
    return response.json()

def main():
    try:
        # URL to extract content from
        url = "https://aimagazine.com/top10/top-10-ai-innovations"
        
        # Check and delete the topic if it exists
        check_and_delete_topic('AI Innovations')

        # Create or get the topic
        topic = create_topic('AI Innovations')
        print(f"Created or found existing topic: {topic['name']}")

        # Create an initial article for the topic
        initial_article = create_initial_article(topic['id'], topic['name'])
        print(f"Created initial article: {initial_article['article']}")

        # Extract content using the html_extractor
        extracted_content = extract_html_content(url)
        if not extracted_content:
            raise Exception("Failed to extract content from URL")
        
        # Format the content properly
        article_id = initial_article['article']['id']
        update_data = {
            'content': extracted_content['main_content'],
            'topic': topic['name'],
            'topic_id': topic['id'],
            'metadata': {
                'source_url': url,
                'title': extracted_content['title'],
                'domain': extracted_content['domain']
            }
        }

        # Debug print
        print("Content to be sent:", update_data)

        updated_article = update_article_with_curator(article_id, update_data['content'], update_data['topic'])
        print(f"Updated article with extracted content: {updated_article}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 