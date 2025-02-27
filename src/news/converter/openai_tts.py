"""
Content converter using OpenAI TTS to generate long-form audio from articles.
"""
from .converter_interface import Converter
from api.db.article_db import get_article
from api.models.topic import Topic
from openai import OpenAI
import os
from typing import List
import numpy as np
import wave
import io
from pydub import AudioSegment

class OpenAITTS(Converter):
    
    @staticmethod
    def split_into_sentences(text: str, max_length: int = 4096) -> List[str]:
        """Split text into sentences of maximum length."""
        sentences = []
        current_sentence = []
        current_length = 0
        
        # Split by periods, keeping the period
        parts = text.replace('. ', '.|').split('|')
        
        for part in parts:
            if current_length + len(part) > max_length:
                if current_sentence:
                    sentences.append(' '.join(current_sentence))
                current_sentence = [part]
                current_length = len(part)
            else:
                current_sentence.append(part)
                current_length += len(part)
        
        if current_sentence:
            sentences.append(' '.join(current_sentence))
        
        return sentences

    @classmethod
    def generate_audio(cls, text: str, voice: str = "echo") -> AudioSegment:
        # Initialize as class variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        client = OpenAI(api_key=api_key)

        """Generate audio for a piece of text using OpenAI TTS."""
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3"
        )
        
        # Convert response content to AudioSegment
        audio_segment = AudioSegment.from_mp3(io.BytesIO(response.content))
        return audio_segment

    @staticmethod
    def can_handle(type: str) -> bool:
        return type == 'openai-tts'
    
    @classmethod
    def convert_representation(cls, type: str, topic: Topic) -> bool:
        try:            
            content = topic.representations[-1].content
            
            # Split content into manageable chunks
            sentences = cls.split_into_sentences(content)
            
            # Generate audio for each chunk
            audio_segments = []
            for sentence in sentences:
                audio_segment = cls.generate_audio(sentence)
                audio_segments.append(audio_segment)
            
            # Concatenate all audio segments
            combined_audio = sum(audio_segments)
            
            # Export to bytes buffer
            buffer = io.BytesIO()
            combined_audio.export(buffer, format="mp3")
            audio_bytes = buffer.getvalue()
            
            # Add audio representation
            topic.add_representation(type, audio_bytes.hex(), {"format": "mp3", "binary": True})
            return True
            
        except Exception as e:
            print(f"Error converting {type}: {str(e)}")
            return False 