from typing import Dict, Optional
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

def extract_html_content(url: str) -> Optional[Dict[str, str]]:
    """
    Extracts content from an HTML page.
    
    Args:
        url: The URL of the HTML page to extract content from
        
    Returns:
        Dictionary containing extracted content or None if extraction fails
        {
            'title': str,
            'main_content': str,
            'meta_description': str,
            'domain': str
        }
    """
    try:
        # Fetch the webpage
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract domain
        domain = urlparse(url).netloc
        
        # Extract title
        title = soup.title.string if soup.title else ''
        
        # Extract meta description
        meta_desc = ''
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            meta_desc = meta_tag.get('content', '')
            
        # Extract main content (prioritizing article or main tags)
        main_content = ''
        content_tags = ['article', 'main', 'div[role="main"]', '.content', '#content']
        
        for tag in content_tags:
            content = soup.select_one(tag)
            if content:
                # Remove script and style elements
                for element in content(['script', 'style']):
                    element.decompose()
                main_content = content.get_text(strip=True)
                break
                
        return {
            'title': title,
            'main_content': main_content,
            'meta_description': meta_desc,
            'domain': domain
        }
        
    except Exception as e:
        print(f"Error extracting content: {str(e)}")
        return None 