from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy object
db = SQLAlchemy()

# Import your models here
from .topic import Topic
from .article import Article

# Ensure these are available for import
__all__ = ['db', 'Topic', 'Article']
