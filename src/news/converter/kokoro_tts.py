"""
Content converter using Kokoro TTS to generate long-form audio from articles locally.
"""

import io
from typing import List

from kokoro import KPipeline
from pydub import AudioSegment

from api.models.article import Article
from utils.logging import debug, error, info, warning

from .converter_interface import Converter


class KokoroTTS(Converter):
    """Converter for generating audio using Kokoro TTS."""

    # Default voice
    DEFAULT_VOICE = "bm_george"

    @staticmethod
    def split_into_sentences(text: str, max_length: int = 1000) -> List[str]:
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

        debug("KOKORO_TTS", "Text split", f"Split into {len(sentences)} chunks")
        return sentences

    @classmethod
    def generate_audio(
        cls,
        text: str,
        voice_key: str = DEFAULT_VOICE,
        speed: float = 1.0,
    ) -> AudioSegment:
        """Generate audio for a piece of text using Kokoro TTS.

        Args:
            text: The text to convert to speech
            voice_key: The voice model to use
            speed: Speech speed multiplier (default: 1.0)

        Returns:
            AudioSegment containing the generated speech
        """
        debug(
            "KOKORO_TTS",
            "Generating audio",
            f"Text length: {len(text)}, Voice: {voice_key}, Speed: {speed}",
        )

        try:
            # Initialize pipeline and generate audio
            pipeline = KPipeline(lang_code='a')
            generator = pipeline(text, voice=voice_key, speed=speed)
            
            # Process each chunk and combine audio segments
            audio_segments = []
            for i, (gs, ps, audio) in enumerate(generator):
                debug("KOKORO_TTS", f"Processing chunk {i}", f"Graphemes: {gs}, Phonemes: {ps}")
                
                # Convert numpy array to audio segment
                audio_segment = AudioSegment(
                    audio.tobytes(),
                    frame_rate=24000,  # Kokoro's sample rate
                    sample_width=2,  # 16-bit audio
                    channels=1  # Mono audio
                )
                audio_segments.append(audio_segment)
            
            if not audio_segments:
                raise ValueError("No audio was generated")
                
            # Combine all segments
            combined_audio = sum(audio_segments)
            debug(
                "KOKORO_TTS", "Audio generated", f"Duration: {len(combined_audio)/1000}s"
            )
            
            return combined_audio

        except Exception as e:
            error("KOKORO_TTS", "Audio generation failed", f"Error: {str(e)}")
            raise

    @staticmethod
    def can_handle(content_type: str) -> bool:
        return content_type.startswith("kokoro-tts")

    @classmethod
    def convert_representation(cls, content_type: str, article: Article) -> bool:
        try:
            info("KOKORO_TTS", "Starting conversion", f"Article: {article.title}")

            # Parse voice key and speed from content type if specified
            voice_key = cls.DEFAULT_VOICE
            speed = 1.0
            
            if "/" in content_type:
                parts = content_type.split("/", 1)[1].split(":")
                voice_key = parts[0]
                if len(parts) > 1:
                    try:
                        speed = float(parts[1])
                    except ValueError:
                        warning(
                            "KOKORO_TTS",
                            "Invalid speed value",
                            f"Using default speed: 1.0",
                        )

            # Use the most recent representation's content, or fall back to article content
            if article.representations:
                content = article.representations[-1].content
                info(
                    "KOKORO_TTS",
                    "Using previous representation",
                    f"Type: {article.representations[-1].type}",
                )
            else:
                content = article.content
                info(
                    "KOKORO_TTS",
                    "No previous representations",
                    "Using original article content",
                )

            # Generate audio for the entire content
            combined_audio = cls.generate_audio(content, voice_key, speed)

            # Export to bytes buffer
            buffer = io.BytesIO()
            combined_audio.export(buffer, format="mp3")
            audio_bytes = buffer.getvalue()

            # Add audio representation
            total_duration = len(combined_audio) / 1000  # in seconds
            info(
                "KOKORO_TTS",
                "Conversion complete",
                f"Article: {article.title}, Duration: {total_duration:.1f}s",
            )
            article.add_representation(
                content_type,
                audio_bytes.hex(),
                {"format": "mp3", "binary": True, "extension": "mp3"},
            )
            return True

        except Exception as e:
            error(
                "KOKORO_TTS",
                "Conversion failed",
                f"Article: {article.title}, Error: {str(e)}",
            )
            return False 