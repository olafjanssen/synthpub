"""
Content converter that simply uses the article content as is.
"""

from api.models.article import Article
from utils.logging import error, info

from ..converter.converter_interface import Converter


class Content(Converter):
    @staticmethod
    def can_handle(content_type: str) -> bool:
        return content_type == "content"

    @staticmethod
    def convert_representation(content_type: str, article: Article) -> bool:
        try:
            # This converter specifically uses the original article content directly
            # regardless of previous representations
            info(
                "CONTENT",
                "Using original content",
                f"Article: {article.title}"
            )
            article.add_representation(content_type, article.content)
            return True

        except Exception as e:
            error(
                "CONVERT",
                "Content conversion failed",
                f"Error converting {content_type}: {str(e)}",
            )
            return False
