"""
Audio utilities module for processing and manipulating audio.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
import json
from datetime import datetime
import asyncio
import wave
import pyaudio
import numpy as np
from pathlib import Path
import tempfile
import librosa
import soundfile as sf
from scipy import signal

class AudioUtils:
    """Utilities for audio processing and manipulation."""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        format: int = pyaudio.paFloat32
    ):
        """Initialize audio utilities with configuration."""
        self.logger = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.channels = channels
        self.format = format
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
    
    def convert_format(
        self,
        audio_data: bytes,
        input_format: int,
        output_format: int
    ) -> bytes:
        """Convert audio data between formats."""
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=self._get_dtype(input_format))
            
            # Convert to output format
            output_array = audio_array.astype(self._get_dtype(output_format))
            
            return output_array.tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to convert format: {e}")
            raise
    
    def _get_dtype(self, format: int) -> np.dtype:
        """Get numpy dtype for audio format."""
        format_map = {
            pyaudio.paFloat32: np.float32,
            pyaudio.paInt16: np.int16,
            pyaudio.paInt32: np.int32,
            pyaudio.paInt8: np.int8,
            pyaudio.paUInt8: np.uint8
        }
        return format_map.get(format, np.float32)
    
    def resample(
        self,
        audio_data: bytes,
        input_rate: int,
        output_rate: int
    ) -> bytes:
        """Resample audio data to a different sample rate."""
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Resample
            resampled = librosa.resample(
                audio_array,
                orig_sr=input_rate,
                target_sr=output_rate
            )
            
            return resampled.tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to resample audio: {e}")
            raise
    
    def normalize(self, audio_data: bytes) -> bytes:
        """Normalize audio data."""
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Normalize
            normalized = librosa.util.normalize(audio_array)
            
            return normalized.tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to normalize audio: {e}")
            raise
    
    def apply_filter(
        self,
        audio_data: bytes,
        filter_type: str = "lowpass",
        cutoff_freq: float = 1000.0
    ) -> bytes:
        """Apply a filter to audio data."""
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Design filter
            nyquist = self.sample_rate / 2
            normalized_cutoff = cutoff_freq / nyquist
            
            if filter_type == "lowpass":
                b, a = signal.butter(4, normalized_cutoff, btype='low')
            elif filter_type == "highpass":
                b, a = signal.butter(4, normalized_cutoff, btype='high')
            elif filter_type == "bandpass":
                b, a = signal.butter(4, [normalized_cutoff * 0.8, normalized_cutoff * 1.2], btype='band')
            else:
                raise ValueError(f"Unsupported filter type: {filter_type}")
            
            # Apply filter
            filtered = signal.filtfilt(b, a, audio_array)
            
            return filtered.tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to apply filter: {e}")
            raise
    
    def detect_silence(
        self,
        audio_data: bytes,
        threshold: float = 0.01,
        min_duration: float = 0.1
    ) -> List[Tuple[float, float]]:
        """Detect silence periods in audio data."""
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Calculate energy
            energy = librosa.feature.rms(y=audio_array)[0]
            
            # Find silence periods
            silence_mask = energy < threshold
            silence_regions = []
            
            start = None
            for i, is_silence in enumerate(silence_mask):
                if is_silence and start is None:
                    start = i
                elif not is_silence and start is not None:
                    duration = (i - start) / self.sample_rate
                    if duration >= min_duration:
                        silence_regions.append((
                            start / self.sample_rate,
                            i / self.sample_rate
                        ))
                    start = None
            
            return silence_regions
            
        except Exception as e:
            self.logger.error(f"Failed to detect silence: {e}")
            raise
    
    def trim_silence(
        self,
        audio_data: bytes,
        top_db: float = 20.0,
        frame_length: int = 2048,
        hop_length: int = 512
    ) -> bytes:
        """Trim silence from audio data."""
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Trim silence
            trimmed, _ = librosa.effects.trim(
                audio_array,
                top_db=top_db,
                frame_length=frame_length,
                hop_length=hop_length
            )
            
            return trimmed.tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to trim silence: {e}")
            raise
    
    def extract_features(
        self,
        audio_data: bytes,
        feature_type: str = "mfcc",
        n_mfcc: int = 13
    ) -> np.ndarray:
        """Extract audio features."""
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            if feature_type == "mfcc":
                features = librosa.feature.mfcc(
                    y=audio_array,
                    sr=self.sample_rate,
                    n_mfcc=n_mfcc
                )
            elif feature_type == "spectral":
                features = librosa.feature.spectral_centroid(
                    y=audio_array,
                    sr=self.sample_rate
                )
            elif feature_type == "chroma":
                features = librosa.feature.chroma_stft(
                    y=audio_array,
                    sr=self.sample_rate
                )
            else:
                raise ValueError(f"Unsupported feature type: {feature_type}")
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract features: {e}")
            raise
    
    def save_audio(
        self,
        audio_data: bytes,
        filepath: str,
        format: str = "wav"
    ) -> Dict[str, Any]:
        """Save audio data to file."""
        try:
            # Create directory if it doesn't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Save audio
            sf.write(filepath, audio_array, self.sample_rate)
            
            return {
                'filepath': filepath,
                'duration': len(audio_array) / self.sample_rate,
                'size': len(audio_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to save audio: {e}")
            raise
    
    def load_audio(self, filepath: str) -> bytes:
        """Load audio data from file."""
        try:
            # Load audio
            audio_array, sample_rate = sf.read(filepath)
            
            # Resample if necessary
            if sample_rate != self.sample_rate:
                audio_array = librosa.resample(
                    audio_array,
                    orig_sr=sample_rate,
                    target_sr=self.sample_rate
                )
            
            return audio_array.tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to load audio: {e}")
            raise
    
    def close(self) -> None:
        """Close audio resources."""
        try:
            self.audio.terminate()
            
        except Exception as e:
            self.logger.error(f"Failed to close audio resources: {e}")
            raise 