import pyaudio
import asyncio
from typing import List, Optional
from jarvis.config import FORMAT, CHANNELS, RATE, CHUNK

class Audio:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.mic_stream = self.audio.open(
            format=FORMAT, 
            channels=CHANNELS, 
            rate=RATE, 
            input=True, 
            frames_per_buffer=CHUNK
        )

        self.queues = []
        self._running = False
        self.task = None

    def subscribe(self):
        q = asyncio.Queue()
        self.queues.append(q)
        return q
    
    async def start(self):
        if self._running:
            return # Already running
        self._running = True
        self.task = asyncio.create_task(self._producer())
    
    async def stop(self):
        self._running = False
        if self.task:
            await asyncio.wait([self.task], timeout=2)

    async def _producer(self):
        while self._running:
            try:
                data = await asyncio.to_thread(self.mic_stream.read, CHUNK, exception_on_overflow=False)
                for q in self.queues:
                    await q.put(data)
            except Exception as e:
                if self._running:
                    print(f"Audio error: {e}")
                break
    
    def cleanup(self):
        self.mic_stream.stop_stream()
        self.mic_stream.close()
        self.audio.terminate()
