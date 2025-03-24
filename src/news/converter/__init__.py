"""Converter connector initialization."""

from .content import Content
from .openai_tts import OpenAITTS
from .piper_tts import PiperTTS
from .podcast_episode_rss_converter import PodcastEpisodeRSSConverter
from .prompt import Prompt

# List of all connector classes
CONVERTERS = [
    OpenAITTS,
    PiperTTS,
    Content,
    Prompt,
    PodcastEpisodeRSSConverter,
]

# Connect signals for all converters
for converter in CONVERTERS:
    converter.connect_signals()
