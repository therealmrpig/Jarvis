import numpy as np
import asyncio
from openwakeword.model import Model
from jarvis.config import WAKEWORD_MODEL_PATH, WAKEWORD_THRESHOLD, WW_CHUNK

class WakeWordMonitor:
    def __init__(self, queue):
        self.model = Model(inference_framework="onnx", wakeword_models=[WAKEWORD_MODEL_PATH])
        self.queue = queue
        self.triggered = asyncio.Event()

    def _predict(self, chunk):
        return self.model.predict(chunk)

    def _flush(self):
        # Feed 5 chunks (~400ms) of silence to slightly push out Jarvis's echo
        # without introducing too much latency for the next user input.
        for _ in range(5):
            self.model.predict(np.zeros(WW_CHUNK, dtype=np.int16))

    def _is_triggered(self, predictions):
        for mdl, score in predictions.items():
            if score > WAKEWORD_THRESHOLD:
                return True, mdl, score
        return False, None, None
    
    def clear(self):
        self.triggered.clear()
        self._flush()
        while True:
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break
    
    async def start(self):
        while True:
            data = await self.queue.get()
            if data == None:
                break
            chunk = np.frombuffer(data, dtype=np.int16)
            scores = await asyncio.to_thread(self._predict, chunk)
            if self._is_triggered(scores)[0]:
                self.triggered.set()