"""
Model manager for handling LLM models.
"""

import logging
from typing import Dict, Any, Optional, List
import json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelManager:
    """Manages LLM models and their configurations."""
    
    def __init__(self, model_dir: str = "models"):
        """
        Initialize the model manager.
        
        Args:
            model_dir: Directory to store model files
        """
        self.logger = logging.getLogger(__name__)
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.models = {}
        self.tokenizers = {}
        self.configs = {}
    
    def load_model(
        self,
        model_name: str,
        model_id: str,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ) -> None:
        """
        Load a model and its tokenizer.
        
        Args:
            model_name: Name to identify the model
            model_id: HuggingFace model ID
            device: Device to load the model on
        """
        try:
            self.logger.info(f"Loading model {model_name} ({model_id})")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.tokenizers[model_name] = tokenizer
            
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None
            )
            self.models[model_name] = model
            
            # Load or create config
            config_path = self.model_dir / f"{model_name}_config.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.configs[model_name] = json.load(f)
            else:
                self.configs[model_name] = {
                    "model_id": model_id,
                    "device": device,
                    "max_length": 2048,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 50
                }
                self._save_config(model_name)
            
            self.logger.info(f"Model {model_name} loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    def unload_model(self, model_name: str) -> None:
        """
        Unload a model and its tokenizer.
        
        Args:
            model_name: Name of the model to unload
        """
        try:
            if model_name in self.models:
                del self.models[model_name]
            if model_name in self.tokenizers:
                del self.tokenizers[model_name]
            if model_name in self.configs:
                del self.configs[model_name]
            
            self.logger.info(f"Model {model_name} unloaded")
            
        except Exception as e:
            self.logger.error(f"Failed to unload model {model_name}: {e}")
            raise
    
    def get_model(self, model_name: str) -> Optional[AutoModelForCausalLM]:
        """
        Get a loaded model.
        
        Args:
            model_name: Name of the model to get
            
        Returns:
            The model if loaded, None otherwise
        """
        return self.models.get(model_name)
    
    def get_tokenizer(self, model_name: str) -> Optional[AutoTokenizer]:
        """
        Get a loaded tokenizer.
        
        Args:
            model_name: Name of the model whose tokenizer to get
            
        Returns:
            The tokenizer if loaded, None otherwise
        """
        return self.tokenizers.get(model_name)
    
    def get_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model configuration.
        
        Args:
            model_name: Name of the model whose config to get
            
        Returns:
            The model configuration if loaded, None otherwise
        """
        return self.configs.get(model_name)
    
    def update_config(
        self,
        model_name: str,
        config_updates: Dict[str, Any]
    ) -> None:
        """
        Update model configuration.
        
        Args:
            model_name: Name of the model whose config to update
            config_updates: Dictionary of config updates
        """
        try:
            if model_name not in self.configs:
                raise ValueError(f"Model {model_name} not loaded")
            
            self.configs[model_name].update(config_updates)
            self._save_config(model_name)
            
            self.logger.info(f"Updated config for model {model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to update config for model {model_name}: {e}")
            raise
    
    def _save_config(self, model_name: str) -> None:
        """
        Save model configuration to file.
        
        Args:
            model_name: Name of the model whose config to save
        """
        try:
            config_path = self.model_dir / f"{model_name}_config.json"
            with open(config_path, "w") as f:
                json.dump(self.configs[model_name], f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save config for model {model_name}: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """
        List all loaded models.
        
        Returns:
            List of loaded model names
        """
        return list(self.models.keys()) 