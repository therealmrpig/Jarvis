import urllib.parse
import requests
from jarvis.tools.registry import registry

def _fetch_weather(city: str = "") -> str:
    # Helper function to fetch minimal 1-line weather string from wttr.in.
    try:
        # If city is blank, wttr.in/ detects via IP
        url = f"https://wttr.in/{urllib.parse.quote(city) if city else ''}?format=%C+%t+Rain:+%p"
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return "Error: Could not reach the weather service"
            
        # Cleanup degree symbol for TTS clarity
        clean_text = response.text.strip().replace("°C", " degrees Celsius").replace("°F", " degrees Fahrenheit")
        return clean_text
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

@registry.register(name="get_weather_local", description="Get the current weather for the user's current location (detected automatically via IP). Use this if no specific city is mentioned.")
def get_weather_local() -> str:
    # Fetches local weather automatically.
    return _fetch_weather("")

@registry.register(name="get_weather_for_city", description="Get the current weather for a specific city. You MUST provide the city name as an argument.")
def get_weather_for_city(city: str) -> str:
    # Fetches weather for a specific city provided by the user.
    return _fetch_weather(city)
