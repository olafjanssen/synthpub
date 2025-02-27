"""Converter connector initialization."""
from .bark_tts import BarkTTS
from .content import Content
from .prompt import Prompt
from .openai_tts import OpenAITTS

# List of all connector classes
CONVERTERS = [
    BarkTTS,
    OpenAITTS,
    Content,
    Prompt,
]

# Connect signals for all converters
for converter in CONVERTERS:
    converter.connect_signals()
