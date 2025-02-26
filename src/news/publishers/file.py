"""File system publisher for storing content in files."""
from pathlib import Path
from urllib.parse import unquote, urlparse
from typing import Dict
from .publisher_interface import Publisher
from api.db.article_db import get_article
from api.models.topic import Topic

def parse_file_url(url: str) -> Path:
    """Parse a file:// URL and return the filesystem path."""
    if not url.startswith("file://"):
        raise ValueError("URL must start with file://")
        
    path = url[7:]  # Remove file://
    return Path(unquote(path))  # Handle URL encoding

class FilePublisher(Publisher):
    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme == 'file'
    
    @staticmethod
    def publish_content(url: str, topic: Topic) -> bool:
        try:
            path = parse_file_url(url)
            
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write representation to file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(topic.representation)

            return True
            
        except Exception as e:
            print(f"Error publishing to file {url}: {str(e)}")
            return False 