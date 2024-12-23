"""Process different types of publishers to output content."""
from typing import Dict, List
from .connectors.file import FilePublisher

# List of available publishers
PUBLISHERS = [
    FilePublisher,
]

def publish_content(publish_urls: List[str], content: Dict[str, str]) -> bool:
    """
    Publish content to all specified URLs.
    
    Args:
        publish_urls: List of destination URLs
        content: Dict containing at least 'title' and 'content' keys
        
    Returns:
        bool: True if all publishing succeeded
    """
    success = True
    
    for url in publish_urls:
        published = False
        
        # Find first publisher that can handle this URL
        for publisher in PUBLISHERS:
            if publisher.can_handle(url):
                if publisher.publish_content(url, content):
                    published = True
                
        if not published:
            print(f"No publisher could handle URL: {url}")
            success = False
            
    return success 