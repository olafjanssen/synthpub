"""
YouTube Channel connector for fetching video URLs from a given channel or playlist.
"""
from urllib.parse import urlparse
from typing import List, Dict
from .feed_connector import FeedConnector
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
from urllib.parse import parse_qs

load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv('YOUTUBE_API_KEY')  # Get the key from the .env file
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable not found. Please add it to your .env file.")

def fetch_youtube_videos_playlist(playlist_id: str) -> List[str]:
    """
    Fetch a list of video URLs from a given YouTube playlist ID.
    
    Args:
        playlist_id: The ID of the YouTube playlist
        
    Returns:
        A list of video URLs
    """
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    video_urls = []

    # Fetch videos from the playlist
    playlist_response = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50
    ).execute()

    for item in playlist_response['items']:
        video_id = item['snippet']['resourceId']['videoId']
        video_urls.append(f"https://www.youtube.com/watch?v={video_id}")

    return video_urls

def fetch_youtube_videos_handle(handle: str) -> List[str]:
    """
    Fetch a list of video URLs from a given YouTube channel handle.
    
    Args:
        handle: The handle of the YouTube channel
        
    Returns:
        A list of video URLs
    """
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    video_urls = []

    # Fetch the channel ID from the handle
    channel_response = youtube.channels().list(
        part='id',
        forHandle=handle
    ).execute()

    if not channel_response.get('items'):
        return []

    channel_id = channel_response['items'][0]['id']
    
    # Fetch videos from the channel
    search_response = youtube.search().list(
        part='id,snippet',
        channelId=channel_id,
        maxResults=50,
        type='video'  # Only fetch videos
    ).execute()

    for item in search_response['items']:
        video_id = item['id']['videoId']
        video_urls.append(f"https://www.youtube.com/watch?v={video_id}")

    return video_urls

class YouTubeChannelConnector(FeedConnector):
    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return (
            parsed.netloc in ('www.youtube.com', 'youtube.com') and
            (
                '@' in parsed.path or  # Handle
                'channel' in parsed.path or  # Channel
                'playlist' in parsed.path  # Playlist
            )
        )
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, str]]:
        try:
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            
            if not path_parts:
                return []

            video_urls = []
            title = "YouTube Channel/Playlist"
            
            if 'playlist' in parsed.path:
                playlist_id = parse_qs(parsed.query).get('list', [''])[0]
                if playlist_id:
                    video_urls = fetch_youtube_videos_playlist(playlist_id)
                    title = f"YouTube Playlist: {playlist_id}"
            else:
                handle = path_parts[0]
                if handle.startswith('@'):
                    handle = handle[1:]
                video_urls = fetch_youtube_videos_handle(handle)
                title = f"YouTube Channel: {handle}"
            
            print(video_urls)

            if not video_urls:
                return []
            
            return [{
                'url': url,
                'content': 'YouTube Channel/Playlist Videos:\n' + '\n'.join(video_urls),
                'title': title
            }]
            
        except Exception as e:
            print(f"Error fetching YouTube channel/playlist {url}: {str(e)}")
            return []