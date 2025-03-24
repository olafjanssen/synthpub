"""
Content converter using OpenAI TTS to generate long-form audio from articles.
"""

import io
import os
from typing import List

from openai import OpenAI
from pydub import AudioSegment

from api.models.article import Article
from utils.logging import debug, error, info

from .converter_interface import Converter


class OpenAITTS(Converter):

    @staticmethod
    def split_into_sentences(text: str, max_length: int = 4096) -> List[str]:
        """Split text into sentences of maximum length."""
        sentences = []
        current_sentence = []
        current_length = 0

        # Split by periods, keeping the period
        parts = text.replace(". ", ".|").split("|")

        for part in parts:
            if current_length + len(part) > max_length:
                if current_sentence:
                    sentences.append(" ".join(current_sentence))
                current_sentence = [part]
                current_length = len(part)
            else:
                current_sentence.append(part)
                current_length += len(part)

        if current_sentence:
            sentences.append(" ".join(current_sentence))

        debug("TTS", "Text split", f"Split into {len(sentences)} chunks")
        return sentences

    @classmethod
    def generate_audio(cls, text: str, voice: str = "echo") -> AudioSegment:
        """Generate audio for a piece of text using OpenAI TTS."""
        # Initialize as class variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            error(
                "TTS",
                "API key missing",
                "OPENAI_API_KEY not found in environment variables",
            )
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        client = OpenAI(api_key=api_key)

        debug("TTS", "Generating audio", f"Text length: {len(text)}, Voice: {voice}")
        response = client.audio.speech.create(
            model="tts-1", voice=voice, input=text, response_format="mp3"
        )

        # Convert response content to AudioSegment
        audio_segment = AudioSegment.from_mp3(io.BytesIO(response.content))
        debug("TTS", "Audio generated", f"Duration: {len(audio_segment)/1000}s")
        return audio_segment

    @staticmethod
    def can_handle(content_type: str) -> bool:
        return content_type == "openai-tts"

    @classmethod
    def convert_representation(cls, content_type: str, article: Article) -> bool:
        try:
            info("TTS", "Starting conversion", f"Article: {article.title}")
            
            # Use the most recent representation's content, or fall back to article content
            if article.representations:
                content = article.representations[-1].content
                info("TTS", "Using previous representation", f"Type: {article.representations[-1].type}")
            else:
                content = article.content
                info("TTS", "No previous representations", "Using original article content")

            # Split content into manageable chunks
            sentences = cls.split_into_sentences(content)
            info("TTS", "Processing chunks", f"Chunks: {len(sentences)}")

            # Generate audio for each chunk
            audio_segments = []
            for i, sentence in enumerate(sentences):
                debug("TTS", "Processing chunk", f"{i+1}/{len(sentences)}")
                audio_segment = cls.generate_audio(sentence)
                audio_segments.append(audio_segment)

            # Concatenate all audio segments
            combined_audio = sum(audio_segments)

            # Export to bytes buffer
            buffer = io.BytesIO()
            combined_audio.export(buffer, format="mp3")
            audio_bytes = buffer.getvalue()

            # Add audio representation
            total_duration = len(combined_audio) / 1000  # in seconds
            info(
                "TTS",
                "Conversion complete",
                f"Article: {article.title}, Duration: {total_duration:.1f}s",
            )
            article.add_representation(
                content_type, audio_bytes.hex(), {"format": "mp3", "binary": True}
            )
            return True

        except Exception as e:
            error("TTS", "Conversion failed", f"Article: {article.title}, Error: {str(e)}")
            return False
