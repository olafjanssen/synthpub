"""
Content converter that simply uses the article content as is.
"""

from api.db.article_db import get_article
from api.models.topic import Topic
from utils.logging import error

from ..converter.converter_interface import Converter


class Content(Converter):
    @staticmethod
    def can_handle(content_type: str) -> bool:
        return content_type == "content"

    @staticmethod
    def convert_representation(content_type: str, topic: Topic) -> bool:
        try:
            # Get the specific article
            article = get_article(topic.article)

            topic.add_representation(content_type, article.content)
            return True

        except Exception as e:
            error(
                "CONVERT",
                "Content conversion failed",
                f"Error converting {content_type}: {str(e)}",
            )
            return False
