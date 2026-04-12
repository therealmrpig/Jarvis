from ollama import chat
from jarvis.config import LLM_MODEL, LLM_KEEP_ALIVE, LLM_THINK
from jarvis.tools import registry


class LanguageModel:
    def __init__(self):
        # Store conversation history
        self.message_context = []
    
    def add_user_message(self, message):
        # Add user's input to conversation history
        self.message_context.append({'role': 'user', 'content': message})

    def add_assistant_message(self, message, tool_calls=None):
        # Add assistant's response to conversation history
        msg = {'role': 'assistant', 'content': message}
        if tool_calls:
            msg['tool_calls'] = tool_calls
        self.message_context.append(msg)

    def add_tool_message(self, content):
        # Add tool's output to conversation history
        self.message_context.append({'role': 'tool', 'content': str(content)})
    
    def chat_stream(self):
        # Send conversation to LLM and get response
        # Using stream=True for seamless visual and TTS feedback
        stream = chat(
            model=LLM_MODEL,
            messages=self.message_context,
            tools=registry.get_definitions(),
            stream=True,
            keep_alive=LLM_KEEP_ALIVE,
            think=LLM_THINK
        )

        current_turn_content = ""
        tool_calls = []

        for chunk in stream:
            # Accumulate and yield text content immediately for TTS/UI
            content = chunk['message'].get('content', '')
            if content:
                current_turn_content += content
                yield content
            
            # Accumulate tool calls if present in the stream
            if 'tool_calls' in chunk['message']:
                for tc in chunk['message']['tool_calls']:
                    # Ensure we don't add duplicates if they appear across chunks
                    if tc not in tool_calls:
                        tool_calls.append(tc)

        # If the model called tools, execute them and continue the stream
        if tool_calls:
            # We must add this turn (content + tool_calls) to context
            self.add_assistant_message(current_turn_content, tool_calls=tool_calls)
            
            for tool in tool_calls:
                print(f"\n[Tool] Calling: {tool.function.name}({tool.function.arguments})")
                result = registry.execute(tool.function.name, tool.function.arguments)
                self.add_tool_message(result)
            
            # Recursive call to get the final response after tool execution
            yield from self.chat_stream()
        else:
            # Final message with no further tools, add to history
            if current_turn_content:
                self.add_assistant_message(current_turn_content)
    
    def get_context(self):
        # Return entire conversation history (useful for debugging)
        return self.message_context
    
    def clear_context(self):
        # Clear all conversation history (if you want to start fresh)
        self.message_context.clear()
