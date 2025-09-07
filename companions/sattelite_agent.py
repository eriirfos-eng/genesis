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


import sentinelsat
from skyfield.api import load
import requests
from datetime import datetime

class SatelliteIntel:
    def __init__(self):
        self.sentinel_api = sentinelsat.SentinelAPI('username', 'password')
        self.ts = load.timescale()
        
    async def get_realtime_imagery(self, lat, lon, radius_km=10):
        """Get latest satellite imagery for location"""
        footprint = f"POINT({lon} {lat})"
        products = self.sentinel_api.query(
            footprint,
            date=('NOW-1DAY', 'NOW'),
            platformname='Sentinel-2',
            cloudcoverpercentage=(0, 30)
        )
        return self.download_latest(products)
    
    async def track_satellites_overhead(self, lat, lon):
        """Find all satellites currently overhead"""
        satellites = load.tle_file('https://celestrak.com/NORAD/elements/stations.txt')
        overhead = []
        for sat in satellites:
            topocentric = sat.at(self.ts.now()).subpoint()
            if abs(topocentric.latitude.degrees - lat) < 5:
                overhead.append(sat.name)
        return overhead
