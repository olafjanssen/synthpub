from datetime import datetime
from ..utils.db import db

class Article(db.Model):
    """
    SQLAlchemy model representing an article in the system.

    Attributes:
        id (int): Primary key identifier for the article
        title (str): Title of the article, limited to 200 characters
        content (str): Main content/body of the article
        topic_id (int): Foreign key reference to associated Topic
        created_at (datetime): Timestamp when article was created
        updated_at (datetime): Timestamp when article was last updated
        version (int): Version number of the article, increments with updates
    """
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    version = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        """
        Convert the Article model instance to a dictionary representation.

        Returns:
            dict: Dictionary containing article data with ISO formatted timestamps
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'topic_id': self.topic_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version
        }
