"""
<<<<<<< HEAD
Text-to-speech module for Jarvis.
Handles converting text to speech.
"""

import logging
from typing import Dict, Any, Optional

class VoiceSpeaker:
    """Handles text-to-speech conversion for Jarvis."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the voice speaker with configuration."""
        self.logger = logging.getLogger("jarvis.voice.speaker")
        self.config = config.get("voice", {})
        self.tts_provider = self.config.get("tts_provider", "local")
        self.voice_id = self.config.get("voice_id", "default")
        self.rate = self.config.get("rate", 1.0)
        self.volume = self.config.get("volume", 1.0)
        
        self.logger.info(f"Initializing Voice Speaker with provider: {self.tts_provider}")
        
        # Initialize specific provider
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the chosen TTS provider."""
        if self.tts_provider == "local":
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', int(self.engine.getProperty('rate') * self.rate))
                self.engine.setProperty('volume', self.volume)
                
                # Set voice if specified
                if self.voice_id != "default":
                    voices = self.engine.getProperty('voices')
                    for voice in voices:
                        if self.voice_id in voice.id:
                            self.engine.setProperty('voice', voice.id)
                            break
                
                self.logger.info("Local TTS engine initialized")
            except ImportError:
                self.logger.error("Failed to import pyttsx3. Please install it.")
                raise
        elif self.tts_provider == "elevenlabs":
            try:
                import elevenlabs
                # Set API key from environment
                import os
                api_key = os.getenv("ELEVENLABS_API_KEY")
                if not api_key:
                    self.logger.warning("ELEVENLABS_API_KEY not found in environment variables")
                else:
                    elevenlabs.set_api_key(api_key)
                self.logger.info("ElevenLabs TTS initialized")
            except ImportError:
                self.logger.error("Failed to import elevenlabs. Please install it.")
                raise
        else:
            self.logger.warning(f"Unsupported TTS provider: {self.tts_provider}")
            raise ValueError(f"Unsupported TTS provider: {self.tts_provider}")
    
    def speak(self, text: str, block: bool = True) -> None:
        """
        Convert text to speech and play it.
        
        Args:
            text: The text to speak
            block: Whether to block until speech is complete
        """
        if not text:
            return
            
        self.logger.info(f"Speaking: {text[:50]}...")
        
        if self.tts_provider == "local":
            self._speak_local(text, block)
        elif self.tts_provider == "elevenlabs":
            self._speak_elevenlabs(text)
        else:
            self.logger.error(f"Unsupported TTS provider: {self.tts_provider}")
    
    def _speak_local(self, text: str, block: bool) -> None:
        """Use local TTS engine (pyttsx3)."""
        try:
            if block:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                # Start in a new thread for non-blocking
                import threading
                def speak_thread():
                    self.engine.say(text)
                    self.engine.runAndWait()
                
                thread = threading.Thread(target=speak_thread)
                thread.daemon = True
                thread.start()
        except Exception as e:
            self.logger.error(f"Error in local TTS: {str(e)}")
    
    def _speak_elevenlabs(self, text: str) -> None:
        """Use ElevenLabs for TTS."""
        try:
            import elevenlabs
            import threading
            
            def speak_thread():
                audio = elevenlabs.generate(
                    text=text,
                    voice=self.voice_id,
                    model="eleven_multilingual_v1"
                )
                elevenlabs.play(audio)
            
            thread = threading.Thread(target=speak_thread)
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.logger.error(f"Error in ElevenLabs TTS: {str(e)}")
=======
Text-to-speech module for voice output.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime
import asyncio
import wave
import pyaudio
import numpy as np
from pathlib import Path
import tempfile
import os
from elevenlabs import generate, set_api_key, Voice, VoiceSettings

class TextToSpeech:
    """Handles text-to-speech synthesis."""
    
    def __init__(
        self,
        engine: str = "elevenlabs",
        voice_id: str = "default",
        rate: float = 1.0,
        sample_rate: int = 44100,
        channels: int = 1,
        format: int = pyaudio.paFloat32
    ):
        """Initialize text-to-speech with configuration."""
        self.logger = logging.getLogger(__name__)
        self.engine = engine
        self.voice_id = voice_id
        self.rate = rate
        self.sample_rate = sample_rate
        self.channels = channels
        self.format = format
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # Initialize ElevenLabs
        if engine == "elevenlabs":
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                raise ValueError("ELEVENLABS_API_KEY environment variable not set")
            set_api_key(api_key)
    
    async def synthesize(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Synthesize text to speech."""
        try:
            if self.engine == "elevenlabs":
                return await self._synthesize_elevenlabs(text)
            else:
                raise ValueError(f"Unsupported engine: {self.engine}")
                
        except Exception as e:
            self.logger.error(f"Failed to synthesize speech: {e}")
            raise
    
    async def _synthesize_elevenlabs(self, text: str) -> bytes:
        """Synthesize speech using ElevenLabs."""
        try:
            # Configure voice settings
            voice_settings = VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
            
            # Generate audio
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=self.voice_id,
                    settings=voice_settings
                )
            )
            
            return audio
            
        except Exception as e:
            self.logger.error(f"Failed to synthesize with ElevenLabs: {e}")
            raise
    
    async def play_audio(self, audio_data: bytes) -> None:
        """Play audio data through speakers."""
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True
            )
            
            # Play audio
            self.stream.write(audio_data)
            
            # Clean up
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        except Exception as e:
            self.logger.error(f"Failed to play audio: {e}")
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
    
    async def process_text(
        self,
        text: str,
        play: bool = True,
        save: bool = False,
        filepath: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process text and optionally play/save the audio."""
        try:
            # Synthesize audio
            audio_data = await self.synthesize(text)
            
            result = {
                'text': text,
                'duration': len(audio_data) / (self.sample_rate * self.channels * 2),
                'size': len(audio_data)
            }
            
            # Play audio if requested
            if play:
                await self.play_audio(audio_data)
            
            # Save audio if requested
            if save:
                if filepath is None:
                    filepath = f"data/audio/{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                
                save_result = await self.save_audio(audio_data, filepath)
                result.update(save_result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process text: {e}")
            raise
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices."""
        try:
            if self.engine == "elevenlabs":
                from elevenlabs import voices
                return [
                    {
                        'id': voice.voice_id,
                        'name': voice.name,
                        'category': voice.category,
                        'description': voice.description
                    }
                    for voice in voices()
                ]
            else:
                raise ValueError(f"Unsupported engine: {self.engine}")
                
        except Exception as e:
            self.logger.error(f"Failed to get available voices: {e}")
            raise
    
    async def close(self) -> None:
        """Close audio resources."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            self.audio.terminate()
            
        except Exception as e:
            self.logger.error(f"Failed to close audio resources: {e}")
            raise 
>>>>>>> 05513f3 (Testing-1)
