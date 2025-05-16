"""
Web dashboard application.
"""

import logging
from typing import Dict, Any
from flask import Flask, render_template, jsonify
from pathlib import Path

def create_app(
    template_dir: str = "ui/web_dashboard/templates",
    static_dir: str = "ui/web_dashboard/static"
) -> Flask:
    """
    Create Flask application.
    
    Args:
        template_dir: Directory containing templates
        static_dir: Directory containing static files
        
    Returns:
        Flask application
    """
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create directories if they don't exist
    Path(template_dir).mkdir(parents=True, exist_ok=True)
    Path(static_dir).mkdir(parents=True, exist_ok=True)
    
    @app.route('/')
    def index():
        """Render dashboard index page."""
        return render_template('index.html')
    
    @app.route('/api/status')
    def get_status():
        """Get system status."""
        try:
            # TODO: Implement actual status retrieval
            status = {
                'system': {
                    'status': 'running',
                    'uptime': '1h 30m'
                },
                'components': {
                    'core': {
                        'status': 'active',
                        'memory_usage': '256MB'
                    },
                    'voice': {
                        'status': 'listening',
                        'last_command': 'hello'
                    }
                }
            }
            return jsonify(status)
            
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/logs')
    def get_logs():
        """Get system logs."""
        try:
            # TODO: Implement actual log retrieval
            logs = [
                {
                    'timestamp': '2024-03-20T10:00:00',
                    'level': 'INFO',
                    'message': 'System started'
                },
                {
                    'timestamp': '2024-03-20T10:01:00',
                    'level': 'INFO',
                    'message': 'Voice recognition initialized'
                }
            ]
            return jsonify(logs)
            
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app 