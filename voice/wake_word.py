"""
Wake word detection module.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Generator
import json
from datetime import datetime
import asyncio
import wave
import pyaudio
import numpy as np
import torch
import torchaudio
from pathlib import Path
import tempfile
import os
from transformers import pipeline

class WakeWordDetector:
    """Detects wake words in audio input."""
    
    def __init__(
        self,
        wake_word: str = "jarvis",
        model: str = "vosk",
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        format: int = pyaudio.paFloat32,
        threshold: float = 0.5
    ):
        """Initialize wake word detector with configuration."""
        self.logger = logging.getLogger(__name__)
        self.wake_word = wake_word.lower()
        self.model = model
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = format
        self.threshold = threshold
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # Initialize model
        if model == "vosk":
            from vosk import Model, KaldiRecognizer
            model_path = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-en-us")
            if not os.path.exists(model_path):
                raise ValueError(f"Vosk model not found at {model_path}")
            self.vosk_model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.vosk_model, self.sample_rate)
        elif model == "whisper":
            self.whisper_model = pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-tiny",
                device=0 if torch.cuda.is_available() else -1
            )
    
    async def start_detecting(self) -> Generator[bool, None, None]:
        """Start detecting wake word in audio input."""
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.logger.info("Started detecting wake word")
            
            # Buffer for audio data
            buffer = []
            buffer_size = int(self.sample_rate * 2)  # 2 seconds buffer
            
            # Process audio chunks
            while True:
                data = self.stream.read(self.chunk_size)
                buffer.append(data)
                
                # Keep buffer size limited
                if len(buffer) * self.chunk_size > buffer_size:
                    buffer.pop(0)
                
                # Check for wake word
                if await self._check_wake_word(b''.join(buffer)):
                    yield True
                else:
                    yield False
                
        except Exception as e:
            self.logger.error(f"Failed to start detecting: {e}")
            raise
        finally:
            self.stop_detecting()
    
    def stop_detecting(self) -> None:
        """Stop detecting wake word."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                self.logger.info("Stopped detecting wake word")
                
        except Exception as e:
            self.logger.error(f"Failed to stop detecting: {e}")
            raise
    
    async def _check_wake_word(self, audio_data: bytes) -> bool:
        """Check if wake word is present in audio data."""
        try:
            if self.model == "vosk":
                return await self._check_wake_word_vosk(audio_data)
            elif self.model == "whisper":
                return await self._check_wake_word_whisper(audio_data)
            else:
                raise ValueError(f"Unsupported model: {self.model}")
                
        except Exception as e:
            self.logger.error(f"Failed to check wake word: {e}")
            return False
    
    async def _check_wake_word_vosk(self, audio_data: bytes) -> bool:
        """Check wake word using Vosk."""
        try:
            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').lower()
                return self.wake_word in text
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check wake word with Vosk: {e}")
            return False
    
    async def _check_wake_word_whisper(self, audio_data: bytes) -> bool:
        """Check wake word using Whisper."""
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp:
                # Write WAV file
                with wave.open(temp.name, 'wb') as wav:
                    wav.setnchannels(self.channels)
                    wav.setsampwidth(self.audio.get_sample_size(self.format))
                    wav.setframerate(self.sample_rate)
                    wav.writeframes(audio_data)
                
                # Transcribe audio
                result = self.whisper_model(temp.name)
                text = result['text'].lower()
            
            # Clean up temporary file
            Path(temp.name).unlink()
            
            return self.wake_word in text
            
        except Exception as e:
            self.logger.error(f"Failed to check wake word with Whisper: {e}")
            return False
    
    async def save_audio(
        self,
        audio_data: bytes,
        filepath: str
    ) -> Dict[str, Any]:
        """Save audio data to file."""
        try:
            # Create directory if it doesn't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Write WAV file
            with wave.open(filepath, 'wb') as wav:
                wav.setnchannels(self.channels)
                wav.setsampwidth(self.audio.get_sample_size(self.format))
                wav.setframerate(self.sample_rate)
                wav.writeframes(audio_data)
            
            return {
                'filepath': filepath,
                'duration': len(audio_data) / (self.sample_rate * self.channels * 2),
                'size': len(audio_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to save audio: {e}")
            raise
    
    async def close(self) -> None:
        """Close audio resources."""
        try:
            self.stop_detecting()
            self.audio.terminate()
            
        except Exception as e:
            self.logger.error(f"Failed to close audio resources: {e}")
            raise 