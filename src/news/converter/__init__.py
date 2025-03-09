"""Converter connector initialization."""
from .content import Content
from .prompt import Prompt
from .openai_tts import OpenAITTS
from .podcast_episode_rss_converter import PodcastEpisodeRSSConverter
from .piper_tts import PiperTTS

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
