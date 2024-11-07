from datetime import datetime
from ..utils.db import db

class Topic(db.Model):
    """
    Topic model representing a category or subject area for articles.

    Attributes:
        id (int): Primary key identifier for the topic
        name (str): Unique name of the topic, max length 100 chars
        description (str): Optional description text for the topic
        created_at (datetime): UTC timestamp when topic was created
        articles (relationship): One-to-many relationship with Article model
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    articles = db.relationship('Article', backref='topic', lazy=True)
    
    def to_dict(self):
        """
        Convert topic instance to dictionary representation.

        Returns:
            dict: Dictionary containing topic data including:
                - id: Topic identifier
                - name: Topic name
                - description: Topic description
                - created_at: Creation timestamp in ISO format
                - article_count: Number of articles in this topic
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'article_count': len(self.articles)
        }
