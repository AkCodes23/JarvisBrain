"""
Weather service module for fetching weather information.
"""

import logging
from typing import Dict, Any, Optional, List
import requests
from datetime import datetime

class WeatherService:
    """Service for fetching weather information."""
    
    def __init__(self, api_key: str):
        """Initialize weather service with API key."""
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city."""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'timestamp': datetime.fromtimestamp(data['dt']).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get current weather: {e}")
            raise
    
    def get_forecast(self, city: str, days: int = 5) -> List[Dict[str, Any]]:
        """Get weather forecast for a city."""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # API returns data in 3-hour intervals
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            forecast = []
            
            for item in data['list']:
                forecast.append({
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description'],
                    'wind_speed': item['wind']['speed'],
                    'timestamp': datetime.fromtimestamp(item['dt']).isoformat()
                })
            
            return forecast
            
        except Exception as e:
            self.logger.error(f"Failed to get forecast: {e}")
            raise 