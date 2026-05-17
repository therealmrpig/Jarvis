from ollama import chat
from jarvis.config import LLM_MODEL, LLM_KEEP_ALIVE, LLM_THINK, LLM_SYSTEM_PROMPT


class LanguageModel:
    def __init__(self):
        self._messages = [{'role': 'system', 'content': LLM_SYSTEM_PROMPT}]

    def add_user_message(self, message):
        self._messages.append({'role': 'user', 'content': message})

    def add_assistant_message(self, message, tool_calls=None):
        msg = {'role': 'assistant', 'content': message}
        if tool_calls:
            msg['tool_calls'] = tool_calls
        self._messages.append(msg)

    def add_tool_message(self, content):
        self._messages.append({'role': 'tool', 'content': str(content)})

    def stream(self, tools=None, context=None):
        messages = [self._messages[0]]
        if context:
            messages.append({"role": "system", "content": context})
        messages.extend(self._messages[1:])
        import json; print(f"\n[DEBUG] LLM messages:\n{json.dumps(messages, indent=2, default=str)}\n")
        chat_stream = chat(
            model=LLM_MODEL,
            messages=messages,
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
        self._messages = [self._messages[0]]
