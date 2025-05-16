"""
<<<<<<< HEAD
Speech recognition module for Jarvis.
Handles converting speech to text.
"""

import logging
from typing import Optional, Callable, Dict, Any

class VoiceListener:
    """Handles speech-to-text conversion for Jarvis."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the voice listener with configuration."""
        self.logger = logging.getLogger("jarvis.voice.listener")
        self.config = config.get("voice", {})
        self.stt_provider = self.config.get("stt_provider", "whisper_local")
        self.wake_word = self.config.get("wake_word", "jarvis")
        self.enable_wake_word = self.config.get("enable_wake_word", True)
        
        self.logger.info(f"Initializing Voice Listener with provider: {self.stt_provider}")
        
        # Initialize specific provider
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the chosen STT provider."""
        if self.stt_provider == "whisper_local":
            # Import here to avoid loading model unless needed
            try:
                import whisper
                self.model = whisper.load_model("base")
                self.logger.info("Whisper model loaded successfully")
            except ImportError:
                self.logger.error("Failed to import whisper. Please install it with 'pip install openai-whisper'")
                raise
        elif self.stt_provider == "google":
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
                self.logger.info("Google STT initialized")
            except ImportError:
                self.logger.error("Failed to import speech_recognition. Please install it.")
                raise
        else:
            self.logger.warning(f"Unsupported STT provider: {self.stt_provider}")
            raise ValueError(f"Unsupported STT provider: {self.stt_provider}")
    
    def listen(self, timeout: Optional[int] = None, phrase_time_limit: Optional[int] = None) -> Optional[str]:
        """
        Listen for speech and convert to text.
        
        Args:
            timeout: Time in seconds to wait before giving up
            phrase_time_limit: Maximum length of phrase to capture
            
        Returns:
            Transcribed text or None if nothing detected
        """
        self.logger.info("Listening for speech...")
        
        if self.stt_provider == "whisper_local":
            return self._listen_whisper(timeout, phrase_time_limit)
        elif self.stt_provider == "google":
            return self._listen_google(timeout, phrase_time_limit)
        else:
            self.logger.error(f"Unsupported STT provider: {self.stt_provider}")
            return None
    
    def _listen_whisper(self, timeout: Optional[int], phrase_time_limit: Optional[int]) -> Optional[str]:
        """Use Whisper for speech recognition."""
        import pyaudio
        import numpy as np
        import wave
        from tempfile import NamedTemporaryFile
        import os
        
        # Record audio to temporary file
        with NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # Audio recording parameters
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        # TODO: Implement wake word detection if enabled
        
        # Record audio (simplified version)
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        self.logger.info("Recording...")
        frames = []
        
        # Record for a fixed duration for this example
        # In a real implementation, this would be more sophisticated
        for i in range(0, int(RATE / CHUNK * (phrase_time_limit or 5))):
            data = stream.read(CHUNK)
            frames.append(data)
        
        self.logger.info("Recording finished")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save the audio file
        wf = wave.open(temp_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Transcribe with Whisper
        try:
            result = self.model.transcribe(temp_filename)
            text = result["text"].strip()
            self.logger.info(f"Transcribed: {text}")
            
            # Clean up temp file
            os.unlink(temp_filename)
            
            return text
        except Exception as e:
            self.logger.error(f"Error transcribing audio: {str(e)}")
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            return None
    
    def _listen_google(self, timeout: Optional[int], phrase_time_limit: Optional[int]) -> Optional[str]:
        """Use Google Speech Recognition."""
        import speech_recognition as sr
        
        r = self.recognizer
        with sr.Microphone() as source:
            self.logger.info("Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source)
            self.logger.info("Listening...")
            
            try:
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                self.logger.info("Audio captured, recognizing...")
                
                text = r.recognize_google(audio)
                self.logger.info(f"Recognized: {text}")
                return text
            except sr.WaitTimeoutError:
                self.logger.info("No speech detected within timeout")
                return None
            except sr.UnknownValueError:
                self.logger.info("Could not understand audio")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Error requesting results from Google: {str(e)}")
                return None
=======
Speech listener module for voice input.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Generator
import json
from datetime import datetime
import asyncio
import wave
import pyaudio
import numpy as np
import whisper
import torch
from pathlib import Path
import tempfile

class SpeechListener:
    """Handles speech recognition and audio input."""
    
    def __init__(
        self,
        engine: str = "whisper",
        language: str = "en-US",
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        format: int = pyaudio.paFloat32
    ):
        """Initialize speech listener with configuration."""
        self.logger = logging.getLogger(__name__)
        self.engine = engine
        self.language = language
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = format
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # Initialize Whisper model
        if engine == "whisper":
            self.model = whisper.load_model("base")
            if torch.cuda.is_available():
                self.model = self.model.cuda()
    
    async def start_listening(self) -> Generator[bytes, None, None]:
        """Start listening for audio input."""
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.logger.info("Started listening for audio input")
            
            # Yield audio chunks
            while True:
                data = self.stream.read(self.chunk_size)
                yield data
                
        except Exception as e:
            self.logger.error(f"Failed to start listening: {e}")
            raise
        finally:
            self.stop_listening()
    
    def stop_listening(self) -> None:
        """Stop listening for audio input."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                self.logger.info("Stopped listening for audio input")
                
        except Exception as e:
            self.logger.error(f"Failed to stop listening: {e}")
            raise
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text."""
        try:
            if self.engine == "whisper":
                return await self._transcribe_whisper(audio_data)
            else:
                raise ValueError(f"Unsupported engine: {self.engine}")
                
        except Exception as e:
            self.logger.error(f"Failed to transcribe audio: {e}")
            raise
    
    async def _transcribe_whisper(self, audio_data: bytes) -> str:
        """Transcribe audio using Whisper."""
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
                result = self.model.transcribe(
                    temp.name,
                    language=self.language.split('-')[0]
                )
            
            # Clean up temporary file
            Path(temp.name).unlink()
            
            return result['text']
            
        except Exception as e:
            self.logger.error(f"Failed to transcribe with Whisper: {e}")
            raise
    
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
    
    async def process_audio(
        self,
        audio_data: bytes,
        save: bool = False,
        filepath: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process audio data and optionally save it."""
        try:
            # Transcribe audio
            text = await self.transcribe(audio_data)
            
            result = {
                'text': text,
                'duration': len(audio_data) / (self.sample_rate * self.channels * 2),
                'size': len(audio_data)
            }
            
            # Save audio if requested
            if save:
                if filepath is None:
                    filepath = f"data/audio/{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                
                save_result = await self.save_audio(audio_data, filepath)
                result.update(save_result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process audio: {e}")
            raise
    
    async def close(self) -> None:
        """Close audio resources."""
        try:
            self.stop_listening()
            self.audio.terminate()
            
        except Exception as e:
            self.logger.error(f"Failed to close audio resources: {e}")
            raise 
>>>>>>> 05513f3 (Testing-1)
