"""
Content converter using Piper TTS to generate long-form audio from articles locally.
"""

import io
import json
import os
import tempfile
import time
import wave
from typing import Any, Dict, List, Optional

import requests

# Import Piper library
from piper.voice import PiperVoice
from pydub import AudioSegment

from api.models.topic import Topic
from utils.logging import debug, error, info, warning

from .converter_interface import Converter


class PiperTTS(Converter):

    # Cache for loaded voice models to avoid reloading
    _voice_cache: Dict[str, PiperVoice] = {}

    # Voice database URL
    VOICES_DB_URL = (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json"
    )

    # Base URL for downloading voice models
    VOICE_DOWNLOAD_BASE_URL = (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    )

    # Cache directory for downloaded models
    _cache_dir = os.path.join(tempfile.gettempdir(), "piper_models")

    @classmethod
    def get_voices_database(cls) -> Dict[str, Any]:
        """Get the voices database from Hugging Face."""
        try:
            # Create cache directory if it doesn't exist
            os.makedirs(cls._cache_dir, exist_ok=True)

            # Cache file path
            cache_file = os.path.join(cls._cache_dir, "voices.json")

            # Check if we have a cached version
            if os.path.exists(cache_file) and (
                os.path.getmtime(cache_file) > (time.time() - 86400)
            ):
                # Use cached version if it's less than a day old
                with open(cache_file, "r") as f:
                    return json.load(f)

            # Download the voices database
            debug(
                "PIPER_TTS", "Downloading voices database", f"URL: {cls.VOICES_DB_URL}"
            )
            response = requests.get(cls.VOICES_DB_URL, timeout=30)
            response.raise_for_status()

            # Parse the JSON response
            voices_db = response.json()

            # Cache the database
            with open(cache_file, "w") as f:
                json.dump(voices_db, f)

            return voices_db
        except Exception as e:
            error("PIPER_TTS", "Failed to get voices database", f"Error: {str(e)}")
            # Return empty dict if we can't get the database
            return {}

    @classmethod
    def list_available_voices(cls) -> List[str]:
        """List all available voice models."""
        voices_db = cls.get_voices_database()
        return list(voices_db.keys())

    @classmethod
    def _download_file(cls, url: str, target_path: str) -> bool:
        """Download a single file from URL to target path."""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            error("PIPER_TTS", "Download failed", f"URL: {url}, Error: {str(e)}")
            return False

    @classmethod
    def _get_model_files(cls, voice_info: Dict[str, Any]) -> Dict[str, str]:
        """Get the list of files needed for the voice model."""
        model_files = {}
        for file_type in ["model", "config", "vocoder"]:
            if file_type in voice_info:
                model_files[file_type] = voice_info[file_type]
        return model_files

    @classmethod
    def download_voice_model(cls, voice_key: str) -> Dict[str, str]:
        """Download a voice model from Hugging Face."""
        voices_db = cls.get_voices_database()

        if voice_key not in voices_db:
            raise ValueError(f"Voice '{voice_key}' not found in the voices database")

        voice_info = voices_db[voice_key]
        model_files = cls._get_model_files(voice_info)  # type: ignore

        try:
            # Create voice-specific cache directory
            voice_cache_dir = os.path.join(cls._cache_dir, voice_key)
            os.makedirs(voice_cache_dir, exist_ok=True)

            # Download each required file
            downloaded_files = {}
            for file_type, file_path in model_files.items():
                url = f"{cls.VOICE_DOWNLOAD_BASE_URL}{file_path}"
                target_path = os.path.join(voice_cache_dir, os.path.basename(file_path))

                if cls._download_file(url, target_path):  # type: ignore
                    downloaded_files[file_type] = target_path

            if not downloaded_files:
                raise ValueError("Failed to download any model files")

            return downloaded_files

        except Exception as e:
            error(
                "PIPER_TTS",
                "Model download failed",
                f"Voice: {voice_key}, Error: {str(e)}",
            )
            raise

    @staticmethod
    def split_into_sentences(text: str, max_length: int = 1000) -> List[str]:
        """Split text into sentences of maximum length."""
        sentences = []
        current_sentence: List[str] = []
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

        debug("PIPER_TTS", "Text split", f"Split into {len(sentences)} chunks")
        return sentences

    @classmethod
    def get_voice(cls, voice_key: str = "en_US-lessac-medium") -> PiperVoice:
        """Get or load a Piper voice model."""
        if voice_key in cls._voice_cache:
            return cls._voice_cache[voice_key]

        debug("PIPER_TTS", "Loading voice model", f"Voice: {voice_key}")

        try:
            # Download the model if needed
            model_files = cls.download_voice_model(voice_key)

            # Load the voice model
            voice = PiperVoice.load(model_files["model"])
            cls._voice_cache[voice_key] = voice
            return voice
        except Exception as e:
            error(
                "PIPER_TTS",
                "Failed to load voice model",
                f"Voice: {voice_key}, Error: {str(e)}",
            )
            raise

    @classmethod
    def generate_audio(
        cls,
        text: str,
        voice_key: str = "en_US-lessac-medium",
        speaker_id: Optional[int] = None,
    ) -> AudioSegment:
        """Generate audio for a piece of text using Piper TTS.

        Args:
            text: The text to convert to speech
            voice_key: The voice model to use
            speaker_id: Optional speaker ID for multi-speaker models

        Returns:
            AudioSegment containing the generated speech
        """
        debug(
            "PIPER_TTS",
            "Generating audio",
            f"Text length: {len(text)}, Voice: {voice_key}, Speaker ID: {speaker_id}",
        )

        # Get the voice model
        voice = cls.get_voice(voice_key)

        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_file_path = wav_file.name

        try:
            # Open the WAV file for writing
            with wave.open(wav_file_path, "w") as wav_file:
                # Synthesize audio directly to the WAV file
                voice.synthesize(text, wav_file, speaker_id=speaker_id)

            # Load the generated audio file
            audio_segment = AudioSegment.from_wav(wav_file_path)
            debug(
                "PIPER_TTS", "Audio generated", f"Duration: {len(audio_segment)/1000}s"
            )

            return audio_segment

        except Exception as e:
            error("PIPER_TTS", "Audio generation failed", f"Error: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            try:
                os.unlink(wav_file_path)
            except Exception as e:
                warning(
                    "PIPER_TTS",
                    "Failed to delete temp file",
                    f"Path: {wav_file_path}, Error: {str(e)}",
                )

    @staticmethod
    def can_handle(content_type: str) -> bool:
        return content_type.startswith("piper-tts")

    @classmethod
    def _parse_voice_info(cls, content_type: str) -> tuple[str, Optional[int]]:
        """Parse voice key and speaker ID from content type string."""
        voice_key = "en_US-lessac-medium"
        speaker_id = None

        # Parse type string for voice_key and optional speaker_id
        if "/" in content_type:
            parts = content_type.split("/", 1)[1].split(":")
            voice_key = parts[0]

            # Extract speaker_id if provided
            if len(parts) > 1 and parts[1].isdigit():
                speaker_id = int(parts[1])

        return voice_key, speaker_id

    @classmethod
    def _generate_combined_audio(
        cls, content: str, voice_key: str, speaker_id: Optional[int]
    ) -> tuple[AudioSegment, float]:
        """Generate audio for content by splitting it into chunks and combining them.

        Returns:
            tuple[AudioSegment, float]: The combined audio and its duration in seconds
        """
        # Split content into manageable chunks
        sentences = cls.split_into_sentences(content)
        info("PIPER_TTS", "Processing chunks", f"Chunks: {len(sentences)}")

        # Generate audio for each chunk
        audio_segments = []
        for i, sentence in enumerate(sentences):
            debug("PIPER_TTS", "Processing chunk", f"{i+1}/{len(sentences)}")
            audio_segment = cls.generate_audio(sentence, voice_key, speaker_id)
            audio_segments.append(audio_segment)

        # Concatenate all audio segments
        combined_audio = sum(audio_segments)
        total_duration = len(combined_audio) / 1000  # in seconds

        return combined_audio, total_duration

    @classmethod
    def convert_representation(cls, content_type: str, topic: Topic) -> bool:
        try:
            info("PIPER_TTS", "Starting conversion", f"Topic: {topic.name}")
            content = topic.representations[-1].content

            # Get voice from URL or use default
            voice_key, speaker_id = cls._parse_voice_info(content_type)

            info(
                "PIPER_TTS",
                "Using voice",
                f"Voice: {voice_key}, Speaker ID: {speaker_id}",
            )

            # Generate the combined audio
            combined_audio, total_duration = cls._generate_combined_audio(
                content, voice_key, speaker_id
            )

            # Export to bytes buffer
            buffer = io.BytesIO()
            combined_audio.export(buffer, format="mp3")
            audio_bytes = buffer.getvalue()

            # Add audio representation
            info(
                "PIPER_TTS",
                "Conversion complete",
                f"Topic: {topic.name}, Duration: {total_duration:.1f}s",
            )
            topic.add_representation(
                content_type,
                audio_bytes.hex(),
                {
                    "format": "mp3",
                    "binary": True,
                    "voice": voice_key,
                    "speaker_id": speaker_id,
                    "duration_seconds": total_duration,
                },
            )
            return True

        except Exception as e:
            error(
                "PIPER_TTS",
                "Conversion failed",
                f"Topic: {topic.name}, Error: {str(e)}",
            )
            return False
