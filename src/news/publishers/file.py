"""File system publisher for storing content in files."""
from pathlib import Path
from urllib.parse import unquote, urlparse
from typing import Dict
from .publisher_interface import Publisher
from api.models.topic import Topic
import base64

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
    def write_content(path: Path, content: str, is_binary: bool = False) -> None:
        """Write content to file, handling both text and binary data."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if is_binary:
            # Convert hex string back to bytes
            binary_data = bytes.fromhex(content)
            with open(path, 'wb') as f:
                f.write(binary_data)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    @staticmethod
    def publish_content(url: str, topic: Topic) -> bool:
        try:
            file_path = parse_file_url(url)
            
            # Get the most recent representation
            rep = topic.representations[-1]
            
            # Use metadata to determine format and binary mode
            is_binary = rep.metadata.get('binary', False)
                        
            FilePublisher.write_content(file_path, rep.content, is_binary)
            print(f"Published {rep.type} content to {file_path}")

            return True
            
        except Exception as e:
            print(f"Error publishing to file {url}: {str(e)}")
            return False 