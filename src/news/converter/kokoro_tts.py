"""
Content converter using Kokoro TTS to generate long-form audio from articles locally.
"""

import io
import re
from typing import List

from kokoro import KPipeline
import soundfile as sf
import numpy as np

from api.models.article import Article
from utils.logging import debug, error, info, warning

from .converter_interface import Converter


class KokoroTTS(Converter):
    """Converter for generating audio using Kokoro TTS."""

    # Default voice
    DEFAULT_VOICE = "bm_george"
    # Sample rate for audio
    SAMPLE_RATE = 24000
    # Silence duration in seconds
    SILENCE_DURATION = 0.5

    @staticmethod
    def split_into_sentences(text: str, max_length: int = 1000) -> List[str]:
        """Split text into sentences of maximum length.
        
        Uses regex-based splitting on common sentence endings, with basic handling
        for common abbreviations.
        
        Args:
            text: The text to split into sentences
            max_length: Maximum length of each sentence chunk
            
        Returns:
            List of sentence chunks, each not exceeding max_length
        """
        # First replace common abbreviations with a temporary marker
        abbreviations = {
            'Mr.': 'Mr@',
            'Mrs.': 'Mrs@',
            'Dr.': 'Dr@',
            'Prof.': 'Prof@',
            'St.': 'St@',
            'Ave.': 'Ave@',
            'Blvd.': 'Blvd@',
            'Rd.': 'Rd@',
            'Inc.': 'Inc@',
            'Ltd.': 'Ltd@',
            'Co.': 'Co@',
            'Corp.': 'Corp@',
            'vs.': 'vs@',
            'e.g.': 'eg@',
            'i.e.': 'ie@',
            'etc.': 'etc@',
            'approx.': 'approx@',
            'no.': 'no@'
        }
        
        # Replace abbreviations with markers
        for abbr, marker in abbreviations.items():
            text = text.replace(abbr, marker)
        
        # Split on sentence endings
        sentences = [s.strip() for s in re.split(r'[.!?]\s+', text) if s.strip()]
        
        # Restore abbreviations in each sentence
        for abbr, marker in abbreviations.items():
            sentences = [s.replace(marker, abbr) for s in sentences]
        
        info("KOKORO_TTS", "Text split", f"Split into {len(sentences)} chunks")
        return sentences

    @classmethod
    def generate_audio(
        cls,
        text: str,
        voice_key: str = DEFAULT_VOICE,
        speed: float = 1.0,
    ) -> bytes:
        """Generate audio for a piece of text using Kokoro TTS.

        Args:
            text: The text to convert to speech
            voice_key: The voice model to use
            speed: Speech speed multiplier (default: 1.0)

        Returns:
            bytes containing the generated speech in MP3 format
        """
        debug(
            "KOKORO_TTS",
            "Generating audio",
            f"Text length: {len(text)}, Voice: {voice_key}, Speed: {speed}",
        )

        try:
            # Split text into sentences first
            sentences = cls.split_into_sentences(text)
            info("KOKORO_TTS", "Processing sentences", f"Number of sentences: {len(sentences)}")
            
            # Initialize pipeline
            pipeline = KPipeline(lang_code='a')
            
            # Process each sentence and combine audio segments
            audio_chunks = []
            for i, sentence in enumerate(sentences):
                info("KOKORO_TTS", f"Processing sentence {i+1}/{len(sentences)}", f"Length: {len(sentence)}, {sentence}")
                generator = pipeline(sentence, voice=voice_key, speed=speed)
                
                # Process each chunk from the generator
                for gs, ps, audio in generator:
                    audio_chunks.append(audio)
            
            if not audio_chunks:
                raise ValueError("No audio was generated")
                
            # Create silence array
            silence_samples = int(cls.SILENCE_DURATION * cls.SAMPLE_RATE)
            silence = np.zeros(silence_samples)
            
            # Combine all chunks with silence between them
            combined_audio = []
            for i, chunk in enumerate(audio_chunks):
                combined_audio.append(chunk)
                if i < len(audio_chunks) - 1:  # Don't add silence after the last chunk
                    combined_audio.append(silence)
            
            combined_audio = np.concatenate(combined_audio)
            
            # Convert to MP3 using soundfile and io
            buffer = io.BytesIO()
            sf.write(buffer, combined_audio, cls.SAMPLE_RATE, format='MP3')
            audio_bytes = buffer.getvalue()
            
            info(
                "KOKORO_TTS", 
                "Audio generated", 
                f"Duration: {len(combined_audio)/cls.SAMPLE_RATE:.1f}s"
            )
            
            return audio_bytes

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
            audio_bytes = cls.generate_audio(content, voice_key, speed)

            # Add audio representation
            total_duration = len(audio_bytes) / cls.SAMPLE_RATE  # in seconds
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