"""Converter connector initialization."""

from .content import Content
from .kokoro_tts import KokoroTTS
from .openai_tts import OpenAITTS
from .piper_tts import PiperTTS
from .podcast_episode_rss_converter import PodcastEpisodeRSSConverter
from .prompt import Prompt

# List of all connector classes
CONVERTERS = [
    OpenAITTS,
    PiperTTS,
    KokoroTTS,
    Content,
    Prompt,
    PodcastEpisodeRSSConverter,
]
