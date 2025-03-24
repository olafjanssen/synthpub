"""
YouTube connector for fetching transcripts from YouTube videos, channels, and playlists.
"""

import os
from typing import Any, Dict, List
from urllib.parse import ParseResult, parse_qs, urlparse

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from utils.logging import error, info

from .feed_connector import FeedConnector


def get_api_key():
    """Get YouTube API key from environment variables"""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY environment variable not found in settings")
    return api_key


def fetch_youtube_transcript(video_id: str) -> str:
    """Fetch transcript for a single video ID"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(entry["text"] for entry in transcript)
    except Exception as e:
        error("YOUTUBE", "Transcript fetch failed", str(e))
        return ""


def fetch_youtube_videos_playlist(playlist_id: str) -> List[Dict[str, Any]]:
    """Fetch transcripts from all videos in a playlist"""
    youtube = build("youtube", "v3", developerKey=get_api_key())
    items = []

    try:
        playlist_response = (
            youtube.playlistItems()
            .list(part="snippet", playlistId=playlist_id, maxResults=50)
            .execute()
        )

        for item in playlist_response["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            # For playlist items, we only fetch basic info and mark for further processing
            items.append(
                {
                    "url": video_url,
                    "content": f"YouTube Video: {item['snippet'].get('title', f'Video {video_id}')}",
                    "title": item["snippet"].get("title", f"YouTube Video {video_id}"),
                    "needs_further_processing": True,  # These items need further processing by the YouTube connector
                }
            )

        return items
    except Exception as e:
        error("YOUTUBE", "Playlist fetch failed", str(e))
        return []


def fetch_youtube_videos_handle(handle: str) -> List[Dict[str, Any]]:
    """Fetch transcripts from all videos in a channel"""
    youtube = build("youtube", "v3", developerKey=get_api_key())
    items = []

    try:
        channel_response = (
            youtube.channels().list(part="id", forHandle=handle).execute()
        )

        if not channel_response.get("items"):
            return []

        channel_id = channel_response["items"][0]["id"]

        search_response = (
            youtube.search()
            .list(part="id,snippet", channelId=channel_id, maxResults=50, type="video")
            .execute()
        )

        for item in search_response["items"]:
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            # For channel items, we only fetch basic info and mark for further processing
            items.append(
                {
                    "url": video_url,
                    "content": f"YouTube Video: {item['snippet'].get('title', f'Video {video_id}')}",
                    "title": item["snippet"].get("title", f"YouTube Video {video_id}"),
                    "needs_further_processing": True,  # These items need further processing by the YouTube connector
                }
            )

        return items
    except Exception as e:
        error("YOUTUBE", "Channel fetch failed", str(e))
        return []


def fetch_youtube_videos_channel(channel_id: str) -> List[Dict[str, Any]]:
    """Fetch transcripts from all videos in a channel by channel ID"""
    youtube = build("youtube", "v3", developerKey=get_api_key())
    items = []

    try:
        search_response = (
            youtube.search()
            .list(part="id,snippet", channelId=channel_id, maxResults=50, type="video")
            .execute()
        )

        for item in search_response["items"]:
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            # For channel items, we only fetch basic info and mark for further processing
            items.append(
                {
                    "url": video_url,
                    "content": f"YouTube Video: {item['snippet'].get('title', f'Video {video_id}')}",
                    "title": item["snippet"].get("title", f"YouTube Video {video_id}"),
                    "needs_further_processing": True,  # These items need further processing by the YouTube connector
                }
            )

        return items
    except Exception as e:
        error("YOUTUBE", "Channel fetch failed", str(e))
        return []


def _handle_channel_url(parsed_url: ParseResult) -> List[Dict[str, Any]]:
    """Handle YouTube channel URL."""
    path_parts = [p for p in parsed_url.path.split("/") if p]
    if "@" in parsed_url.path:
        handle = path_parts[0].lstrip("@")
        return fetch_youtube_videos_handle(handle)
    elif "channel" in parsed_url.path:
        channel_id = path_parts[-1]
        return fetch_youtube_videos_channel(channel_id)
    return []


def _handle_playlist_url(parsed_url: ParseResult) -> List[Dict[str, Any]]:
    """Handle YouTube playlist URL."""
    playlist_id = parse_qs(parsed_url.query).get("list", [""])[0]
    return fetch_youtube_videos_playlist(playlist_id) if playlist_id else []


def _handle_video_url(parsed_url: ParseResult) -> List[Dict[str, Any]]:
    """Handle YouTube video URL."""
    video_id = None
    if parsed_url.netloc == "youtu.be":
        video_id = parsed_url.path[1:]
    else:
        video_id = parse_qs(parsed_url.query).get("v", [""])[0]

    if not video_id:
        return []

    try:
        transcript = fetch_youtube_transcript(video_id)
        return [
            {
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "content": transcript,
                "needs_further_processing": False,
            }
        ]
    except Exception as e:
        error(
            "YOUTUBE", "Transcript fetch failed", f"Video: {video_id}, Error: {str(e)}"
        )
        return []


class YouTubeConnector(FeedConnector):
    # Cache for 6 hours
    cache_expiration = 6 * 3600

    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return (
            parsed.netloc in ("www.youtube.com", "youtube.com", "youtu.be")
            or parsed.scheme == "youtube"
        )

    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, Any]]:
        """Fetch content from YouTube URL."""
        info("YOUTUBE", "Fetching content", url)
        try:
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split("/") if p]

            # Handle different URL types
            if "playlist" in parsed.path:
                return _handle_playlist_url(parsed)
            elif "@" in parsed.path or "channel" in parsed.path:
                return _handle_channel_url(parsed)
            else:
                return _handle_video_url(parsed)

        except Exception as e:
            error("YOUTUBE", "Content fetch failed", f"URL: {url}, Error: {str(e)}")
            return []
