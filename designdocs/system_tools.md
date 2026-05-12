# `jarvis/tools/system_tools.py` Deep Dive

## Purpose
This script contains basic system-level tools that allow Jarvis to provide accurate real-world context like current time and date.

## Tools

### `get_time()`
*   **Description:** Returns the current local time in `HH:MM:SS` format.
*   **Logic:** Uses `datetime.now()`.
*   **Registry Metadata:** Includes an "ALWAYS call" instruction in the description. This is a prompt-engineering trick to ensure the LLM doesn't hallucinate the time based on its training data.

### `get_date()`
*   **Description:** Returns the current local date in `YYYY-MM-DD` format.
*   **Logic:** Uses `datetime.now()`.

## Implementation Detail
*   **Decorator:** Uses `@registry.register` to automatically expose these functions to the `LanguageModel`.
*   **Stateless:** These functions are pure and stateless, making them extremely reliable.
