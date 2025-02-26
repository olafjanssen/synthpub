"""
Content converter taking the content from the most recent article version. (default)
"""
from .converter_interface import Converter
from api.db.article_db import get_article
from api.models.topic import Topic

class Content(Converter):
    @staticmethod
    def can_handle(type: str) -> bool:
        return type == 'content'
    
    @staticmethod
    def convert_content(type: str, topic: Topic) -> bool:
        try:
            # Get the specific article
            article = get_article(topic.article)

            topic.representation = article.content
            return True
            
        except Exception as e:
            print(f"Error converting {type}: {str(e)}")
            return False 