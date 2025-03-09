#!/usr/bin/env python3
"""
Example script demonstrating how to use the PiperTTS module with dynamic voice model downloading.
"""
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from news.converter.piper_tts import PiperTTS
from api.models.topic import Topic, Representation
from datetime import datetime

def main():
    """Main function to demonstrate PiperTTS usage."""
    # Create a sample topic with text content
    sample_text = """
    Piper is a fast, local neural text to speech system that sounds great and is optimized for the Raspberry Pi 4.
    It uses a model trained with VITS and exported to the ONNX runtime.
    This example demonstrates how to use the PiperTTS module to convert text to speech with dynamic voice model downloading.
    """
    
    # List available voices
    print("Fetching available voices...")
    available_voices = PiperTTS.list_available_voices()
    print(f"Found {len(available_voices)} available voices")
    
    # Select a voice (default to English if available)
    selected_voice = "en_US-lessac-medium"
    if available_voices:
        # Print some available voices
        print("\nSome available voices:")
        for i, voice in enumerate(available_voices[:5]):
            print(f"  - {voice}")
        
        # Try to find an English voice
        english_voices = [v for v in available_voices if v.startswith("en_")]
        if english_voices:
            selected_voice = english_voices[0]
    
    print(f"\nUsing voice: {selected_voice}")
    
    # Create a topic with a text representation
    topic = Topic(
        id="example-topic",
        name="Piper TTS Example",
        description="An example topic for demonstrating Piper TTS",
        feed_urls=[],
        representations=[
            Representation(
                type="text",
                content=sample_text,
                created_at=datetime.now()
            )
        ],
        metadata={"voice": selected_voice}
    )
    
    # Convert the text representation to audio using PiperTTS
    print(f"\nConverting text to speech for topic: {topic.name}")
    print(f"This will automatically download the voice model if needed.")
    success = PiperTTS.convert_representation("piper-tts", topic)
    
    if success:
        print("\nConversion successful!")
        
        # Get the audio representation
        audio_rep = next((r for r in topic.representations if r.type == "piper-tts"), None)
        if audio_rep:
            # Save the audio to a file
            audio_bytes = bytes.fromhex(audio_rep.content)
            output_file = "piper_tts_example.mp3"
            with open(output_file, "wb") as f:
                f.write(audio_bytes)
            print(f"Audio saved to {output_file}")
            
            # Print metadata
            print("\nAudio metadata:")
            for key, value in audio_rep.metadata.items():
                print(f"  - {key}: {value}")
    else:
        print("\nConversion failed!")

if __name__ == "__main__":
    main() 