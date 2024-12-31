"""
YouTube connector for fetching transcripts from YouTube videos, channels, and playlists.
"""
from urllib.parse import urlparse, parse_qs
from typing import List, Dict
from .feed_connector import FeedConnector
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
from api.signals import news_feed_update_requested, news_feed_item_found

# ... existing environment setup code ...
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable not found. Please add it to your .env file.")

def fetch_youtube_transcript(video_id: str) -> str:
    """Fetch transcript for a single video ID"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(entry["text"] for entry in transcript)
    except Exception as e:
        print(f"Error fetching transcript for video ID {video_id}: {str(e)}")
        return ""

def fetch_youtube_videos_playlist(playlist_id: str) -> List[Dict[str, str]]:
    """Fetch transcripts from all videos in a playlist"""
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    items = []

    try:
        playlist_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50
        ).execute()

        for item in playlist_response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            transcript = fetch_youtube_transcript(video_id)
            if transcript:
                items.append({
                    'url': video_url,
                    'content': transcript,
                    'title': item['snippet'].get('title', f'YouTube Video {video_id}')
                })
        
        return items
    except Exception as e:
        print(f"Error fetching playlist {playlist_id}: {str(e)}")
        return []

def fetch_youtube_videos_handle(handle: str) -> List[Dict[str, str]]:
    """Fetch transcripts from all videos in a channel"""
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    items = []

    try:
        channel_response = youtube.channels().list(
            part='id',
            forHandle=handle
        ).execute()

        if not channel_response.get('items'):
            return []

        channel_id = channel_response['items'][0]['id']
        
        search_response = youtube.search().list(
            part='id,snippet',
            channelId=channel_id,
            maxResults=50,
            type='video'
        ).execute()

        for item in search_response['items']:
            video_id = item['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            transcript = fetch_youtube_transcript(video_id)
            if transcript:
                items.append({
                    'url': video_url,
                    'content': transcript,
                    'title': item['snippet'].get('title', f'YouTube Video {video_id}')
                })

        return items
    except Exception as e:
        print(f"Error fetching channel {handle}: {str(e)}")
        return []

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
        print(f"Fetching content for {url}")
        try:
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]

            # Handle channel/playlist URLs
            if path_parts and ('@' in parsed.path or 'channel' in parsed.path or 'playlist' in parsed.path):
                if 'playlist' in parsed.path:
                    playlist_id = parse_qs(parsed.query).get('list', [''])[0]
                    return fetch_youtube_videos_playlist(playlist_id) if playlist_id else []
                else:
                    handle = path_parts[0]
                    if handle.startswith('@'):
                        handle = handle[1:]
                    return fetch_youtube_videos_handle(handle)

            # Handle single video URLs
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
            print(f"Error fetching YouTube content {url}: {str(e)}")
            return []

YouTubeConnector.connect_signals() 