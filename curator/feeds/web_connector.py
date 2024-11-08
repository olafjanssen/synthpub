"""
Web connector for fetching and parsing webpage content.
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict

def fetch_webpage(url: str) -> Dict[str, str]:
    """
    Fetch content from a webpage and extract useful text.
    
    Args:
        url: The webpage URL to fetch
        
    Returns:
        Dict containing title and main content
    """
    response = requests.get(url)
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