"""Process different types of feeds and aggregate their content."""
from typing import List, Dict, Tuple
from urllib.parse import urlparse
from .web_connector import fetch_webpage
from .rss_connector import fetch_rss_links
from api.models.feed_item import FeedItem

def process_feeds(feed_urls: List[str]) -> Tuple[List[Dict[str, str]], List[FeedItem]]:
    """
    Process a list of feed URLs and return their content and feed items.
    
    Args:
        feed_urls: List of URLs (both direct web and RSS feeds)
        
    Returns:
        Tuple of (content_list, feed_items)
    """
    all_content = []
    feed_items = []
    
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
                        
                        # Create feed item
                        feed_items.append(FeedItem.create(
                            url=entry['link'],
                            content=content['content']
                        ))
                    except Exception as e:
                        print(f"Error fetching RSS entry content from {entry['link']}: {str(e)}")
                        
            else:
                # Handle direct web URL
                content = fetch_webpage(url)
                all_content.append(content)
                
                # Create feed item
                feed_items.append(FeedItem.create(
                    url=url,
                    content=content['content']
                ))
                
        except Exception as e:
            print(f"Error processing feed {url}: {str(e)}")
            
    return all_content, feed_items