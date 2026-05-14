# `jarvis/tools/weather_tools.py` Deep Dive

## Purpose
This script provides Jarvis with live weather information by interfacing with external APIs.

## Implementation Details

### Internal Helper: `_fetch_weather(city: str)`
*   **Provider:** Uses `wttr.in`, a console-oriented weather service.
*   **Logic:**
    *   Constructs a URL with specific format parameters (`%C+%t+Rain:+%p`).
    *   Performs a synchronous `requests.get` call.
    *   **TTS Optimization:** Replaces symbols like `°C` with "degrees Celsius" to ensure the `TextToSpeech` engine pronounces the units correctly.
    *   **Error Handling:** Returns a descriptive string if the network is down or the city is not found.

### Tools

1.  **`get_weather_local()`**
    *   Calls `_fetch_weather("")`.
    *   `wttr.in` automatically detects the user's location based on their IP address.

2.  **`get_weather_for_city(city: str)`**
    *   Accepts a city name from the LLM.
    *   Passes it to the helper for a targeted search.

## Design Considerations
*   **Blocking I/O:** `requests.get` is a blocking call. Because tools are executed via `registry.execute` which is called within the `LanguageModel` (itself often wrapped in a thread in `engine.py`), it does not block the UI but does block the completion of the current LLM turn.
*   **No API Keys:** By using `wttr.in`, the system maintains a "low-friction" setup for the user.
