"""Process different types of feeds and aggregate their content."""
from typing import List, Dict, Tuple
from urllib.parse import urlparse, parse_qs
from .web_connector import fetch_webpage
from .rss_connector import fetch_rss_links
from .youtube_connector import fetch_youtube_transcript
from .youtube_channel_connector import fetch_youtube_videos_playlist, fetch_youtube_videos_handle
from api.models.feed_item import FeedItem
from .file_connector import fetch_files

def process_feeds(feed_urls: List[str]) -> Tuple[List[Dict[str, str]], List[FeedItem]]:
    """
    Process a list of feed URLs and return their content and feed items.
    
    Args:
        feed_urls: List of URLs (both direct web, RSS feeds, and YouTube)
        
    Returns:
        Tuple of (content_list, feed_items)
    """
    all_content = []
    feed_items = []
    
    for url in feed_urls:
        try:
            parsed_url = urlparse(url)
            
            print(parsed_url)

            if parsed_url.scheme == 'file':
                # Handle local files
                file_contents = fetch_files(url)
                for content in file_contents:
                    all_content.append(content)
                    feed_items.append(FeedItem.create(
                        url=content['url'],
                        content=content['content']
                    ))
                    
            elif parsed_url.scheme == 'feed':
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
                        
            elif 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
                if 'playlist' in parsed_url.path or '@' in parsed_url.path:
                    # Handle YouTube channel or playlist URL
                    if 'playlist' in parsed_url.path:
                        playlist_id = parse_qs(parsed_url.query)['list'][0]
                        video_urls = fetch_youtube_videos_playlist(playlist_id)
                    else:
                        handle_id = parsed_url.path.split('@')[-1]
                        video_urls = fetch_youtube_videos_handle(handle_id)
                    
                    for video_url in video_urls:
                        # Fetch transcript for each video
                        transcript = fetch_youtube_transcript(video_url.split('v=')[-1])
                        all_content.append(transcript)
                        
                        # Create feed item
                        feed_items.append(FeedItem.create(
                            url=video_url,
                            content=transcript
                        ))
                else:
                    # Handle YouTube video URL
                    video_id = parse_qs(parsed_url.query).get('v', [None])[0] or parsed_url.path.split('/')[-1]
                    if video_id:
                        transcript = fetch_youtube_transcript(video_id)
                        all_content.append(transcript)
                        
                        # Create feed item
                        feed_items.append(FeedItem.create(
                            url=url,
                            content=transcript
                        ))
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

    print(all_content)     
    return all_content, feed_items