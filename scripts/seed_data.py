import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from api import create_app
from api.models.topic import Topic
from api.models.article import Article
from api.utils.db import db

def seed_database():
    """Seed the database with initial data."""
    app = create_app()
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Create topics
        topics_data = [
            {
                'name': 'Game Mechanics',
                'description': 'Core concepts and systems that form the foundation of gameplay.'
            },
            {
                'name': 'Level Design',
                'description': 'Principles and practices of creating engaging game environments.'
            },
            {
                'name': 'Game Economics',
                'description': 'In-game economy design and balance systems.'
            }
        ]
        
        topics = {}
        for topic_data in topics_data:
            topic = Topic(**topic_data)
            db.session.add(topic)
            db.session.flush()  # Get ID before commit
            topics[topic.name] = topic
            print(f"Created topic: {topic.name}")
        
        # Create articles
        articles_data = [
            {
                'title': 'Understanding Game Loops',
                'content': '''A game loop is the central component of any game engine. 
                It continuously processes user input, updates game state, and renders 
                the game world to the screen. This article explores different 
                implementations and their pros and cons.''',
                'topic_id': topics['Game Mechanics'].id
            },
            {
                'title': 'Principles of Level Flow',
                'content': '''Good level design guides players through the game space 
                intuitively. This article discusses techniques for creating natural 
                flow in level design, including environmental storytelling, 
                breadcrumbing, and spatial progression.''',
                'topic_id': topics['Level Design'].id
            },
            {
                'title': 'Virtual Economy Basics',
                'content': '''Creating balanced in-game economies requires understanding 
                of both economic principles and player psychology. This article covers 
                fundamental concepts of virtual economies, including currency sinks, 
                faucets, and market dynamics.''',
                'topic_id': topics['Game Economics'].id
            }
        ]
        
        for article_data in articles_data:
            article = Article(**article_data)
            db.session.add(article)
            print(f"Created article: {article.title}")
        
        # Commit all changes
        db.session.commit()
        print("\nDatabase seeding completed successfully!")

if __name__ == '__main__':
    seed_database() 