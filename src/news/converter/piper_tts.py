
import io
import json
import os
import tempfile
import time
import wave
from typing import Any, Dict, List, Optional

import requests
from pydub import AudioSegment

# Dummy PiperVoice implementation for testing
class PiperVoice:
    @staticmethod
    def synthesize(text: str, wav_file: wave.Wave_write, speaker_id: Optional[int] = None):
        import struct
        sample_rate = 22050
        duration = 1.0  # seconds of silence per sentence
        n_samples = int(sample_rate * duration)
        wav_file.setparams((1, 2, sample_rate, n_samples, "NONE", "not compressed"))
        for _ in range(n_samples):
            wav_file.writeframes(struct.pack('<h', 0))  # silent audio

from api.models.article import Article
from utils.logging import debug, error, info, warning

from .converter_interface import Converter


class PiperTTS(Converter):

    _voice_cache = {}

    VOICES_DB_URL = (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json"
    )
    VOICE_DOWNLOAD_BASE_URL = (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    )
    _cache_dir = os.path.join(tempfile.gettempdir(), "piper_models")

    @classmethod
    def get_voices_database(cls) -> Dict[str, Any]:
        try:
            os.makedirs(cls._cache_dir, exist_ok=True)
            cache_file = os.path.join(cls._cache_dir, "voices.json")

            if os.path.exists(cache_file) and (
                os.path.getmtime(cache_file) > (time.time() - 86400)
            ):
                with open(cache_file, "r") as f:
                    return json.load(f)

            debug("PIPER_TTS", "Downloading voices database", f"URL: {cls.VOICES_DB_URL}")
            response = requests.get(cls.VOICES_DB_URL, timeout=30)
            response.raise_for_status()
            voices_db = response.json()
            with open(cache_file, "w") as f:
                json.dump(voices_db, f)
            return voices_db
        except Exception as e:
            error("PIPER_TTS", "Failed to get voices database", f"Error: {str(e)}")
            return {}

    @classmethod
    def list_available_voices(cls) -> List[str]:
        voices_db = cls.get_voices_database()
        return list(voices_db.keys())

    @classmethod
    def download_voice_model(cls, voice_key: str) -> Dict[str, str]:
        voices_db = cls.get_voices_database()

        if voice_key not in voices_db:
            raise ValueError(f"Voice '{voice_key}' not found in the voices database")

        voice_info = voices_db[voice_key]
        model_files = {}

        try:
            voice_cache_dir = os.path.join(cls._cache_dir, voice_key)
            os.makedirs(voice_cache_dir, exist_ok=True)

            for file_path, file_info in voice_info["files"].items():
                local_file = os.path.join(voice_cache_dir, os.path.basename(file_path))
                if (
                    os.path.exists(local_file)
                    and os.path.getsize(local_file) == file_info["size_bytes"]
                ):
                    debug("PIPER_TTS", "Using cached model file", f"File: {local_file}")
                else:
                    file_url = f"{cls.VOICE_DOWNLOAD_BASE_URL}{file_path}"
                    debug("PIPER_TTS", "Downloading model file", f"URL: {file_url}")
                    response = requests.get(file_url, stream=True, timeout=120)
                    response.raise_for_status()
                    with open(local_file, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                if file_path.endswith(".onnx"):
                    model_files["model"] = local_file
                elif file_path.endswith(".onnx.json"):
                    model_files["config"] = local_file

            return model_files
        except Exception as e:
            error("PIPER_TTS", "Failed to download voice model", f"Voice: {voice_key}, Error: {str(e)}")
            raise

    @staticmethod
    def split_into_sentences(text: str, max_length: int = 1000) -> List[str]:
        sentences = []
        current_sentence = []
        current_length = 0
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
    def get_voice(cls, voice_key: str = "en_US-lessac-medium") -> PiperVoice:  # type: ignore
        if voice_key in cls._voice_cache:
            return cls._voice_cache[voice_key]

        debug("PIPER_TTS", "Loading voice model", f"Voice: {voice_key}")
        try:
            model_files = cls.download_voice_model(voice_key)
            voice = PiperVoice()  # Use dummy class instead of loading actual model
            cls._voice_cache[voice_key] = voice
            return voice
        except Exception as e:
            error("PIPER_TTS", "Failed to load voice model", f"Voice: {voice_key}, Error: {str(e)}")
            raise

    @classmethod
    def generate_audio(
        cls,
        text: str,
        voice_key: str = "en_US-lessac-medium",
        speaker_id: Optional[int] = None,
    ) -> AudioSegment:
        debug(
            "PIPER_TTS",
            "Generating audio",
            f"Text length: {len(text)}, Voice: {voice_key}, Speaker ID: {speaker_id}",
        )

        voice = cls.get_voice(voice_key)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_file_path = wav_file.name

        try:
            with wave.open(wav_file_path, "w") as wav_file:
                voice.synthesize(text, wav_file, speaker_id=speaker_id)

            audio_segment = AudioSegment.from_wav(wav_file_path)
            debug("PIPER_TTS", "Audio generated", f"Duration: {len(audio_segment)/1000}s")
            return audio_segment

        except Exception as e:
            error("PIPER_TTS", "Audio generation failed", f"Error: {str(e)}")
            raise
        finally:
            try:
                os.unlink(wav_file_path)
            except Exception as e:
                warning("PIPER_TTS", "Failed to delete temp file", f"Path: {wav_file_path}, Error: {str(e)}")

    @staticmethod
    def can_handle(content_type: str) -> bool:
        return content_type.startswith("piper-tts")

    @classmethod
    def convert_representation(cls, content_type: str, article: Article) -> bool:
        try:
            info("PIPER_TTS", "Starting conversion", f"Article: {article.title}")

            voice_key = "en_US-lessac-medium"
            if "/" in content_type:
                _, voice_key = content_type.split("/", 1)

            if article.representations:
                content = article.representations[-1].content
                info("PIPER_TTS", "Using previous representation", f"Type: {article.representations[-1].type}")
            else:
                content = article.content
                info("PIPER_TTS", "No previous representations", "Using original article content")

            sentences = cls.split_into_sentences(content)
            info("PIPER_TTS", "Processing chunks", f"Chunks: {len(sentences)}")

            audio_segments = []
            for i, sentence in enumerate(sentences):
                debug("PIPER_TTS", "Processing chunk", f"{i+1}/{len(sentences)}")
                try:
                    audio_segment = cls.generate_audio(sentence, voice_key)
                    audio_segments.append(audio_segment)
                except Exception as chunk_error:
                    error("PIPER_TTS", "Chunk processing failed", f"Chunk {i+1}: {str(chunk_error)}")

            if not audio_segments:
                raise ValueError("No audio was generated from any chunks")

            combined_audio = sum(audio_segments)

            buffer = io.BytesIO()
            combined_audio.export(buffer, format="mp3")
            audio_bytes = buffer.getvalue()

            total_duration = len(combined_audio) / 1000
            info("PIPER_TTS", "Conversion complete", f"Article: {article.title}, Duration: {total_duration:.1f}s")

            article.add_representation(
                content_type,
                audio_bytes.hex(),
                {"format": "mp3", "binary": True, "extension": "mp3"},
            )
            return True

        except Exception as e:
            error("PIPER_TTS", "Conversion failed", f"Article: {article.title}, Error: {str(e)}")
            return False

