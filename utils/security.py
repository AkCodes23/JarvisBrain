"""
Security utility module for handling encryption and security features.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import json
from cryptography.fernet import Fernet
import logging

class SecurityManager:
    """Manages security features and encryption."""
    
    def __init__(self, encryption_key: Optional[str] = None, ssl_verify: bool = True):
        """Initialize security manager with configuration."""
        self.logger = logging.getLogger(__name__)
        self.ssl_verify = ssl_verify
        
        # Initialize encryption
        if encryption_key:
            self.fernet = Fernet(encryption_key.encode())
        else:
            self.fernet = Fernet.generate_key()
            self.fernet = Fernet(self.fernet)
    
    def encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt sensitive data."""
        try:
            return self.fernet.encrypt(json.dumps(data).encode())
        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt sensitive data."""
        try:
            return json.loads(self.fernet.decrypt(encrypted_data).decode())
        except Exception as e:
            self.logger.error(f"Failed to decrypt data: {e}")
            raise
    
    def save_encrypted_data(self, data: Dict[str, Any], filepath: str) -> None:
        """Save encrypted data to file."""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(self.encrypt_data(data))
        except Exception as e:
            self.logger.error(f"Failed to save encrypted data: {e}")
            raise
    
    def load_encrypted_data(self, filepath: str) -> Dict[str, Any]:
        """Load encrypted data from file."""
        try:
            with open(filepath, 'rb') as f:
                return self.decrypt_data(f.read())
        except Exception as e:
            self.logger.error(f"Failed to load encrypted data: {e}")
            raise 