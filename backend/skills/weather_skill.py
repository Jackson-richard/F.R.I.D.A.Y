import requests
from typing import Dict, Any
from skills.base_skill import BaseSkill

class WeatherSkill(BaseSkill):
    name = "get_weather"
    description = "Get the current weather for a specific city or location."
    parameters = {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city or location to get the weather for."
            }
        },
        "required": ["location"]
    }

    def execute(self, location: str, **kwargs) -> str:
        try:
            # wttr.in format 3 gives a nice short text summary
            res = requests.get(f"https://wttr.in/{location}?format=%l:+%C,+%t.+Wind:+%w,+Humidity:+%h", timeout=5)
            if res.status_code == 200:
                return f"Weather data: {res.text.strip()}"
            return f"Could not fetch weather for {location}. Status: {res.status_code}"
        except Exception as e:
            return f"Weather API error: {e}"
