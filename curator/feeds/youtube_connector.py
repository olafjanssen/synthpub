"""
YouTube connector for fetching transcripts from YouTube videos.
"""
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List

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