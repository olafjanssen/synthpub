"""
YouTube Channel connector for fetching video URLs from a given channel or playlist.
"""
from googleapiclient.discovery import build
from typing import List
import os

API_KEY = os.getenv('YOUTUBE_API_KEY')  # Get the key from the .env file

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
        maxResults=50  # Adjust as needed
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

    print(channel_response)

    if channel_response['items']:
        channel_id = channel_response['items'][0]['id']
        # Fetch videos from the channel
        search_response = youtube.search().list(
            part='id,snippet',
            channelId=channel_id,
            maxResults=50  # Adjust as needed
        ).execute()

        for item in search_response['items']:
            if item['id']['kind'] == 'youtube#video':
                video_id = item['id']['videoId']
                video_urls.append(f"https://www.youtube.com/watch?v={video_id}")

    return video_urls