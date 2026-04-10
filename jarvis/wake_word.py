import numpy as np
from openwakeword.model import Model
from jarvis.config import CHUNK, WAKEWORD_MODEL_PATH, WAKEWORD_THRESHOLD

class WakeWordDetector:
    def __init__(self):
        self.model = Model(inference_framework="onnx", wakeword_models=[WAKEWORD_MODEL_PATH])

    def predict(self, audio_frame):
        return self.model.predict(audio_frame)

    def clear_buffer(self):
        # Feed 5 chunks (~400ms) of silence to slightly push out Jarvis's echo
        # without introducing too much latency for the next user input.
        for _ in range(5):
            self.model.predict(np.zeros(CHUNK, dtype=np.int16))

    def is_triggered(self, predictions):
        for mdl, score in predictions.items():
            if score > WAKEWORD_THRESHOLD:
                return True, mdl, score
        return False, None, None