"""Converter connector initialization."""
from .content import Content
from .prompt import Prompt
from .openai_tts import OpenAITTS
from .podcast_episode_rss_converter import PodcastEpisodeRSSConverter

# List of all connector classes
CONVERTERS = [
    OpenAITTS,
    Content,
    Prompt,
    PodcastEpisodeRSSConverter,
]

# Connect signals for all converters
for converter in CONVERTERS:
    converter.connect_signals()
