import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
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
)

completion = client.chat.completions.create(
    model="openai/gpt-oss-20b:together",
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
)

print(completion.choices[0].message)
import pyowm
import meteostat
from datetime import datetime
import numpy as np

class WeatherIntel:
    def __init__(self):
        self.owm = pyowm.OWM('your-api-key')
        
    async def get_hyperlocal_weather(self, lat, lon):
        """Ventusky-level weather precision"""
        mgr = self.owm.weather_manager()
        
        # Current conditions
        current = mgr.weather_at_coords(lat, lon).weather
        
        # Hourly forecast (next 48h)
        forecast = mgr.forecast_at_coords(lat, lon, '3h')
        
        # Weather radar data
        radar = self.get_radar_data(lat, lon)
        
        return {
            'current': {
                'temp': current.temperature('celsius')['temp'],
                'humidity': current.humidity,
                'pressure': current.pressure['press'],
                'wind_speed': current.wind()['speed'],
                'wind_direction': current.wind()['deg'],
                'clouds': current.clouds,
                'visibility': current.visibility_distance
            },
            'forecast_48h': [self.parse_forecast_hour(f) for f in forecast],
            'radar': radar,
            'alerts': self.get_weather_alerts(lat, lon)
        }
    
    def get_radar_data(self, lat, lon):
        """Real-time weather radar (like Ventusky)"""
        # NOAA radar API integration
        url = f"https://api.weather.gov/points/{lat},{lon}/forecast/hourly"
        response = requests.get(url).json()
        return response
