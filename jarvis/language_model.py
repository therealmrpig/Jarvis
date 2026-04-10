from ollama import chat
from jarvis.config import LLM_MODEL, LLM_KEEP_ALIVE, LLM_THINK


class LanguageModel:
    def __init__(self):
        # Store conversation history so model remembers previous exchanges
        self.message_context = []
    
    def add_user_message(self, message):
        # Add user's input to conversation history
        self.message_context.append({'role': 'user', 'content': message})
    
    def add_assistant_message(self, message):
        # Add assistant's response to conversation history
        self.message_context.append({'role': 'assistant', 'content': message})
    
    def chat_stream(self):
        # Send conversation to LLM and get streamed response
        # Returns generator that yields chunks of the response one by one
        stream = chat(
            model=LLM_MODEL,
            messages=self.message_context,
            stream=True,
            keep_alive=LLM_KEEP_ALIVE,
            think=LLM_THINK
        )
        # Yield each chunk from the stream
        for chunk in stream:
            yield chunk['message']['content']
    
    def get_context(self):
        # Return entire conversation history (useful for debugging)
        return self.message_context
    
    def clear_context(self):
        # Clear all conversation history (if you want to start fresh)
        self.message_context.clear()
