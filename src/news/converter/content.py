"""
Content converter that simply uses the article content as is.
"""
from ..converter.converter_interface import Converter
from api.models.topic import Topic
from api.db.article_db import get_article
from utils.logging import error

class Content(Converter):
    @staticmethod
    def can_handle(type: str) -> bool:
        return type == "content"
    
    @staticmethod
    def convert_representation(type: str, topic: Topic) -> bool:
        try:
            # Get the specific article
            article = get_article(topic.article)

            topic.add_representation(type, article.content)
            return True
            
        except Exception as e:
            error("CONVERT", "Content conversion failed", f"Error converting {type}: {str(e)}")
            return False 