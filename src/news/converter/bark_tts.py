"""
Content converter using Bark TTS to generate long-form audio from articles.
"""
from .converter_interface import Converter
from api.db.article_db import get_article
from api.models.topic import Topic
from transformers import AutoProcessor, AutoModel
import torch
import torchaudio
import os
from typing import List
import numpy as np
import io
class BarkTTS(Converter):
    # Initialize models and processor once
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoProcessor.from_pretrained("suno/bark-small")
    model = AutoModel.from_pretrained("suno/bark-small", torch_dtype=torch.float32).to(device)
    os.makedirs("output/audio", exist_ok=True)
    
    @staticmethod
    def split_into_sentences(text: str, max_length: int = 200) -> List[str]:
        """Split text into sentences of maximum length."""
        sentences = []
        current = []
        length = 0
        
        for part in text.replace('. ', '.|').split('|'):
            if length + len(part) > max_length and current:
                sentences.append(' '.join(current))
                current = [part]
                length = len(part)
            else:
                current.append(part)
                length += len(part)
                
        if current:
            sentences.append(' '.join(current))
            
        return sentences

    @staticmethod
    def generate_audio(text: str, voice_preset: str = "v2/en_speaker_6") -> np.ndarray:
        """Generate audio for a piece of text."""
        print(f"Generating audio for text: {text}")
        # Process the text and create inputs
        inputs = BarkTTS.processor(
            text=text,
            voice_preset=voice_preset,
            return_tensors="pt"
        ).to(BarkTTS.device)
        
        # Create attention mask (all 1s since we're not padding)
        attention_mask = torch.ones_like(inputs.input_ids)
        
        # Generate audio with explicit parameters
        speech_values = BarkTTS.model.generate(
            input_ids=inputs.input_ids,
            attention_mask=attention_mask,
            pad_token_id=BarkTTS.processor.tokenizer.pad_token_id,
            eos_token_id=BarkTTS.processor.tokenizer.eos_token_id
        )
        return speech_values.cpu().numpy().squeeze()

    @staticmethod
    def can_handle(type: str) -> bool:
        return type == 'bark-tts'
    
    @staticmethod
    def convert_content(type: str, topic: Topic) -> bool:
        try:
            # Generate audio chunks for each sentence
            audio_chunks = [
                BarkTTS.generate_audio(sentence) 
                for sentence in BarkTTS.split_into_sentences(topic.representations[-1].content)
            ]
            
            # Combine audio and convert to bytes
            combined = np.concatenate(audio_chunks)
            buffer = io.BytesIO()
            
            torchaudio.save(
                buffer,
                torch.tensor(combined).unsqueeze(0),
                sample_rate=24000,
                format="mp3"
            )
            
            # Add audio representation
            audio_bytes = buffer.getvalue()
            topic.add_representation("audio", audio_bytes.hex(), {"format": "mp3", "binary": True})
            
            return True
            
        except Exception as e:
            print(f"Error converting {type}: {str(e)}")
            return False