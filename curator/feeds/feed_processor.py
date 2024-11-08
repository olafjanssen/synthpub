"""Process different types of feeds and aggregate their content."""
from typing import List, Dict
from urllib.parse import urlparse
from .web_connector import fetch_webpage
from .rss_connector import fetch_rss_links

def process_feeds(feed_urls: List[str]) -> List[Dict[str, str]]:
    """
    Process a list of feed URLs and return their content.
    
    Args:
        feed_urls: List of URLs (both direct web and RSS feeds)
        
    Returns:
        List of dicts containing content from all sources
    """
    all_content = []
    
    for url in feed_urls:
        try:
            parsed_url = urlparse(url)
            
            if parsed_url.scheme == 'feed':
                # Handle RSS feed
                actual_url = f"https://{parsed_url.netloc}{parsed_url.path}"
                entries = fetch_rss_links(actual_url)
                
                # Fetch content for each RSS entry
                for entry in entries:
                    try:
                        content = fetch_webpage(entry['link'])
                        all_content.append(content)
                    except Exception as e:
                        print(f"Error fetching RSS entry content from {entry['link']}: {str(e)}")
                        
            else:
                # Handle direct web URL
                content = fetch_webpage(url)
                all_content.append(content)
                
        except Exception as e:
            print(f"Error processing feed {url}: {str(e)}")
            
    return all_content 