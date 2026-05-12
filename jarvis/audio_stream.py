import pyaudio
import asyncio
from typing import List, Optional
from jarvis.config import FORMAT, CHANNELS, RATE, READ_SIZE_FOR_VAD

class AudioStream:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.mic_stream = self.audio.open(
            format=FORMAT, 
            channels=CHANNELS, 
            rate=RATE, 
            input=True, 
            frames_per_buffer=READ_SIZE_FOR_VAD
        )
        self.queues: List[asyncio.Queue] = []
        self.listening = False

    async def _producer(self):
        """Background task that reads audio from hardware and puts it into subscriber queues."""
        while self.listening:
            try:
                # Read from hardware in a thread to avoid blocking the loop
                data = await asyncio.to_thread(self.mic_stream.read, READ_SIZE_FOR_VAD, exception_on_overflow=False)
                if self.listening:
                    for q in self.queues:
                        await q.put(data)
            except Exception as e:
                if self.listening:
                    print(f"Audio producer error: {e}")
                break

    async def start_listening(self):
        """Starts the background audio producer task."""
        if not self.listening:
            self.listening = True
            asyncio.create_task(self._producer())

    def stop_listening(self):
        """Stops the background audio producer task and sends sentinels to all queues."""
        self.listening = False
        # Put sentinel to all queues
        for q in self.queues:
            try:
                q.put_nowait(None)
            except Exception:
                pass

    def get_new_queue(self) -> asyncio.Queue:
        """Creates and returns a new subscriber queue."""
        q = asyncio.Queue()
        self.queues.append(q)
        return q

    def clear_queue(self, queue: asyncio.Queue):
        """Removes all items from the specified queue."""
        while not queue.empty():
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    def read(self, frames: int = READ_SIZE_FOR_VAD, exception_on_overflow: bool = False) -> bytes:
        return self.mic_stream.read(frames, exception_on_overflow=exception_on_overflow)

    def get_read_available(self) -> int:
        return self.mic_stream.get_read_available()

    def flush_buffer(self):
        try:
            # Only read if the stream is active to avoid hangs
            if self.mic_stream.is_active():
                available = self.mic_stream.get_read_available()
                if available > 0:
                    self.mic_stream.read(available, exception_on_overflow=False)
        except Exception:
            pass

    def close(self):
        try:
            self.stop_listening()
            self.mic_stream.stop_stream()
            self.mic_stream.close()
        except Exception:
            pass

    def terminate(self):
        try:
            self.audio.terminate()
        except Exception:
            pass

    def cleanup(self):
        self.close()
        self.terminate()