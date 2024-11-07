import requests

BASE_URL = 'http://localhost:5000/api'

def create_topic(name):
    response = requests.post(f'{BASE_URL}/topics', json={'name': name})
    response.raise_for_status()
    return response.json()

def create_article(title, content, topic_id):
    response = requests.post(f'{BASE_URL}/articles', json={
        'title': title,
        'content': content,
        'topic_id': topic_id
    })
    response.raise_for_status()
    return response.json()

def synthesize_article(content, topic, topic_id):
    response = requests.post(f'{BASE_URL}/articles/synthesize', json={
        'content': content,
        'topic': topic,
        'topic_id': topic_id
    })
    response.raise_for_status()
    return response.json()

def update_article_by_topic(topic_id):
    response = requests.post(f'{BASE_URL}/articles/update-by-topic/{topic_id}')
    response.raise_for_status()
    return response.json()

def main():
    # Create a new topic
    topic = create_topic('AI Innovations')
    print('Created Topic:', topic)

    # Create a new article
    article = create_article('AI in 2023', 'Exploring AI advancements in 2023.', topic['id'])
    print('Created Article:', article)

    # Synthesize a new article using AI Curator
    synthesized_article = synthesize_article('AI content', 'AI Innovations', topic['id'])
    print('Synthesized Article:', synthesized_article)

    # Update the article by topic
    updated_article = update_article_by_topic(topic['id'])
    print('Updated Article:', updated_article)

if __name__ == '__main__':
    main() 