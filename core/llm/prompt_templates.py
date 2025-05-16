"""
Prompt templates for LLM interactions.
"""

import logging
from typing import Dict, Any, Optional
import json
from pathlib import Path
import jinja2

class PromptTemplates:
    """Manages prompt templates for LLM interactions."""
    
    def __init__(self, templates_dir: str = "config/prompts"):
        """
        Initialize prompt templates.
        
        Args:
            templates_dir: Directory containing prompt templates
        """
        self.logger = logging.getLogger(__name__)
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Load templates
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all prompt templates from the templates directory."""
        try:
            for template_file in self.templates_dir.glob("*.j2"):
                template_name = template_file.stem
                self.templates[template_name] = self.env.get_template(template_file.name)
            
            self.logger.info(f"Loaded {len(self.templates)} prompt templates")
            
        except Exception as e:
            self.logger.error(f"Failed to load prompt templates: {e}")
            raise
    
    def get_template(self, template_name: str) -> Optional[jinja2.Template]:
        """
        Get a prompt template by name.
        
        Args:
            template_name: Name of the template to get
            
        Returns:
            The template if found, None otherwise
        """
        return self.templates.get(template_name)
    
    def render_template(
        self,
        template_name: str,
        **kwargs: Any
    ) -> str:
        """
        Render a prompt template with the given variables.
        
        Args:
            template_name: Name of the template to render
            **kwargs: Variables to pass to the template
            
        Returns:
            Rendered prompt text
        """
        try:
            template = self.get_template(template_name)
            if not template:
                raise ValueError(f"Template not found: {template_name}")
            
            return template.render(**kwargs)
            
        except Exception as e:
            self.logger.error(f"Failed to render template {template_name}: {e}")
            raise
    
    def create_template(
        self,
        template_name: str,
        template_content: str
    ) -> None:
        """
        Create a new prompt template.
        
        Args:
            template_name: Name for the new template
            template_content: Content of the template
        """
        try:
            template_path = self.templates_dir / f"{template_name}.j2"
            
            with open(template_path, "w") as f:
                f.write(template_content)
            
            # Reload templates
            self._load_templates()
            
            self.logger.info(f"Created new template: {template_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to create template {template_name}: {e}")
            raise
    
    def delete_template(self, template_name: str) -> None:
        """
        Delete a prompt template.
        
        Args:
            template_name: Name of the template to delete
        """
        try:
            template_path = self.templates_dir / f"{template_name}.j2"
            
            if template_path.exists():
                template_path.unlink()
                
                # Remove from loaded templates
                if template_name in self.templates:
                    del self.templates[template_name]
                
                self.logger.info(f"Deleted template: {template_name}")
            else:
                raise FileNotFoundError(f"Template not found: {template_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to delete template {template_name}: {e}")
            raise
    
    def list_templates(self) -> Dict[str, str]:
        """
        List all available prompt templates.
        
        Returns:
            Dictionary mapping template names to their content
        """
        try:
            templates = {}
            for template_name, template in self.templates.items():
                templates[template_name] = template.render()
            return templates
            
        except Exception as e:
            self.logger.error(f"Failed to list templates: {e}")
            raise 