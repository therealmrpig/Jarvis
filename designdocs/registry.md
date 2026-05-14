# `jarvis/tools/registry.py` Deep Dive

## Purpose
The `ToolRegistry` provides a centralized, automated system for extending Jarvis's capabilities. It translates standard Python functions into the complex JSON schemas required by LLMs for "Function Calling."

## Class: `ToolRegistry`

### `__init__(self)`
*   Initializes a dictionary `self.tools` to store function references and their metadata.

### `register(self, name: str, description: str)`
A decorator that simplifies tool addition.
1.  **Input:** Takes a unique name and a clear description (this description is what the LLM sees to decide when to use the tool).
2.  **Logic:** 
    *   Wraps the target function.
    *   Calls `_generate_schema` to introspect the function.
    *   Stores the function and its generated definition in the registry.

### `_generate_schema(self, func: Callable) -> dict`
This is the "magic" of the registry. It uses the `inspect` module to perform reflection on the Python function.
1.  **Signature Analysis:** Reads the function's parameters and their type hints.
2.  **Type Mapping:** Translates Python types (`int`, `str`, `bool`, etc.) to their JSON Schema equivalents.
3.  **Requirement Detection:** If a parameter doesn't have a default value in Python, the registry marks it as "required" in the JSON schema.
4.  **Output:** Produces a structured dictionary that Ollama/OAI models can consume.

### `get_definitions(self) -> List[Dict]`
*   Returns the list of all registered tool definitions. 
*   This is called by `LanguageModel` every time it sends a prompt to Ollama.

### `execute(self, name: str, arguments: Dict) -> Any`
1.  **Lookup:** Finds the function in the registry by name.
2.  **Invocation:** Calls the function using "star-kwargs" (`**arguments`), passing the values provided by the LLM.
3.  **Error Handling:** Catches any exceptions within the tool and returns them as a string so the LLM can "see" the error and potentially try a different approach.

## Architectural Value
*   **Decoupling:** Tools are isolated from the core engine. You can add a `calculator` tool or a `home_automation` tool by just adding a file to the `tools/` folder.
*   **Type Safety:** By leveraging Python type hints, the registry ensures the LLM provides the correct data types.
