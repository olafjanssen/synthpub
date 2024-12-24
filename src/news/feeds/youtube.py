"""
YouTube connector for fetching transcripts from YouTube videos.
"""
from urllib.parse import urlparse, parse_qs
from typing import List, Dict
from .feed_connector import FeedConnector
from youtube_transcript_api import YouTubeTranscriptApi
from api.signals import news_feed_update_requested, news_feed_item_found

class YouTubeConnector(FeedConnector):
    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return (
            parsed.netloc in ('www.youtube.com', 'youtube.com', 'youtu.be') or
            parsed.scheme == 'youtube'
        )
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, str]]:
        try:
            # Extract video ID from URL
            parsed = urlparse(url)
            if parsed.netloc == 'youtu.be':
                video_id = parsed.path[1:]
            else:
                query = parse_qs(parsed.query)
                video_id = query.get('v', [''])[0]
            
            if not video_id:
                return []
                
            transcript = fetch_youtube_transcript(video_id)
            return [{
                'url': url,
                'content': transcript,
                'title': f'YouTube Video {video_id}'
            }] if transcript else []
            
        except Exception as e:
            print(f"Error fetching YouTube transcript {url}: {str(e)}")
            return []

def fetch_youtube_transcript(video_id: str) -> str:
    """
    Fetch the transcript for a given YouTube video ID and return it as a single string.
    
    Args:
        video_id: The ID of the YouTube video
        
    Returns:
        A string containing the full transcript text
    """
    try:
        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Concatenate the transcript text into a single string
        full_transcript = " ".join(entry["text"] for entry in transcript)
        
        return full_transcript
    except Exception as e:
        print(f"Error fetching transcript for video ID {video_id}: {str(e)}")
        return "" 

YouTubeConnector.connect_signals() 