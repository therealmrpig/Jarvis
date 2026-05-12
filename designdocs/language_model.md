# `jarvis/language_model.py` Deep Dive

## Purpose
The `LanguageModel` class serves as the interface to the local Ollama LLM. It manages conversation history (memory) and implements a recursive streaming logic to handle complex Tool Calling (Function Calling) scenarios.

## Class: `LanguageModel`

### Context Management
*   **`self.message_context`**: A list of dictionaries following the standard ChatML format (`role`, `content`, `tool_calls`).
*   **`add_user_message` / `add_assistant_message` / `add_tool_message`**: Helper methods to append structured data to the context.

### `chat_stream(self)`
This is a complex generator that handles the LLM's streaming output and interleaved tool execution.

1.  **Ollama Request:** Calls `ollama.chat` with `stream=True`. It passes the `message_context` and the list of available tool definitions from the `registry`.
2.  **Stream Iteration:**
    *   **Text Accumulation:** As text chunks arrive, they are yielded immediately. This allows the `Engine` to start synthesizing the first sentence while the model is still generating the second.
    *   **Tool Call Accumulation:** If the model decides to call a tool, it provides a `tool_calls` object. These are collected into a local list.
3.  **Tool Execution Logic:**
    *   If `tool_calls` are present at the end of the stream, it first adds the assistant's partial message to the context.
    *   It then iterates through each tool call, executing the corresponding Python function via `registry.execute`.
    *   The result of each tool is added to the context as a `role: tool` message.
4.  **Recursion:** After executing tools, it calls `yield from self.chat_stream()`. This allows the model to see the tool results and provide a final verbal answer (or call more tools).

## Optimization & Trade-offs
*   **Recursive Streaming:** The recursive pattern is powerful as it supports multi-step reasoning (e.g., "Find the temperature and then tell me if it's hot"). However, it must be handled carefully to avoid infinite loops if a model hallucinates tool calls.
*   **Local-First:** By using Ollama with a `keep_alive` of `-1`, the model remains in VRAM, significantly reducing the "Time to First Word" for subsequent interactions.
*   **Markdown Sanitization:** It currently yields raw text. In `text_to_speech.py`, markdown characters like `*` are stripped to prevent the TTS from attempting to "speak" the punctuation.

## Efficiency Note
*   The use of a generator ensures that the system memory footprint for the response text is minimal, as chunks are processed and then discarded or moved to long-term context.
