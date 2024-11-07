from datetime import datetime
from typing import Dict, List, Optional
from ..models.article import Article
from ..models.topic import Topic
from ..utils.db import db
from uuid import uuid4

class ArticleService:
    @staticmethod
    def get_all_articles(topic_id: Optional[int] = None) -> List[Article]:
        """
        Retrieve all articles, optionally filtered by topic.
        """
        query = Article.query
        if topic_id:
            query = query.filter_by(topic_id=topic_id)
        return query.order_by(Article.created_at.desc()).all()

    @staticmethod
    def get_article_by_id(article_id: int) -> Optional[Article]:
        """
        Retrieve a specific article by ID.
        """
        return Article.query.get(article_id)

    @staticmethod
    def create_article(data: Dict) -> Article:
        """
        Create a new article.
        """
        article = Article(
            title=data['title'],
            content=data['content'],
            topic_id=data['topic_id'],
            version=1
        )
        db.session.add(article)
        db.session.commit()
        return article

    @staticmethod
    def update_article(article_id: int, data: Dict) -> Optional[Article]:
        """
        Update an existing article, creating a new version.
        """
        article = Article.query.get(article_id)
        if not article:
            return None

        # Create new version
        new_article = Article(
            title=data.get('title', article.title),
            content=data.get('content', article.content),
            topic_id=article.topic_id,
            version=article.version + 1
        )
        
        db.session.add(new_article)
        db.session.commit()
        return new_article

    @staticmethod
    def delete_article(article_id: int) -> bool:
        """
        Delete an article.
        """
        article = Article.query.get(article_id)
        if article:
            db.session.delete(article)
            db.session.commit()
            return True
        return False

def trigger_content_update(topic: Topic) -> str:
    """
    Trigger an async content update for a topic.
    Returns a task ID for status tracking.
    """
    task_id = str(uuid4())
    # Here you would typically queue a background task
    # For now, we'll just return the task ID
    return task_id
