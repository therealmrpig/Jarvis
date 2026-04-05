from ollama import chat
from ollama import ChatResponse

stream = chat(
    model='jarvis-gemma-v1',
    messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
    stream=True,
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)
