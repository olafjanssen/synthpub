"""
Web connector for fetching and parsing webpage content.
"""
from urllib.parse import urlparse
from typing import Dict, List
from .feed_connector import FeedConnector
import requests
from bs4 import BeautifulSoup
# Chrome user agent string
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def fetch_webpage(url: str) -> Dict[str, str]:
    """
    Fetch content from a webpage and extract useful text.
    
    Args:
        url: The webpage URL to fetch
        
    Returns:
        Dict containing title and main content
    """
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get title
    title = soup.title.string if soup.title else ''
    
    # Get main content (basic implementation)
    # Remove script and style elements
    for script in soup(['script', 'style']):
        script.decompose()
    
    # Get text and clean it up
    text = ' '.join(soup.stripped_strings)
    
    return {
        'title': title.strip(),
        'content': text.strip(),
        'url': url
    } 

class WebConnector(FeedConnector):
    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https')
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, str]]:
        try:
            content = fetch_webpage(url)  # Your existing function
            return [content]
        except Exception as e:
            print(f"Error fetching webpage {url}: {str(e)}")
            return []