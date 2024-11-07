import requests

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
        # Check and delete the topic if it exists
        check_and_delete_topic('AI Innovations')

        # Create or get the topic
        topic = create_topic('AI Innovations')
        print(f"Created or found existing topic: {topic['name']}")

        # # Create an initial article for the topic
        initial_article = create_initial_article(topic['id'], topic['name'])
        print(f"Created initial article: {initial_article['article']}")

        # Update the article using the curator service
        article_id = initial_article['article']['id']
        content = "Updated content for the article"
        topic_name = topic['name']

        updated_article = update_article_with_curator(article_id, content, topic_name)
        print(f"Updated article: {updated_article}")

    except requests.exceptions.HTTPError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 