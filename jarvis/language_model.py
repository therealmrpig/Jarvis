from ollama import chat
from jarvis.config import LLM_MODEL, LLM_KEEP_ALIVE, LLM_THINK


class LanguageModel:
    def __init__(self):
        # Store conversation history
        self._messages = []
    
    def add_user_message(self, message):
        # Add user's input to conversation history
        self._messages.append({'role': 'user', 'content': message})

    def add_assistant_message(self, message, tool_calls=None):
        # Add assistant's response to conversation history
        msg = {'role': 'assistant', 'content': message}
        if tool_calls:
            msg['tool_calls'] = tool_calls
        self._messages.append(msg)

    def add_tool_message(self, content):
        # Add tool's output to conversation history
        self._messages.append({'role': 'tool', 'content': str(content)})
    
    def stream(self, tools=None):
        chat_stream = chat(
            model=LLM_MODEL,
            messages=self._messages,
            tools=tools,
            stream=True,
            keep_alive=LLM_KEEP_ALIVE,
            think=LLM_THINK
        )
        for chunk in chat_stream:
            msg = chunk["message"]
            out = {}
            if msg.get("content"):
                out["content"] = msg["content"]
            if msg.get("tool_calls"):
                out["tool_calls"] = msg["tool_calls"]
            if out:
                yield out
    
    def clear(self):
        # Clear all conversation history (if you want to start fresh)
        self._messages.clear()
