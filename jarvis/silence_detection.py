import numpy as np
import threading
from silero_vad_lite import SileroVAD
from jarvis.config import RATE, VAD_THRESHOLD, VAD_SILENCE_FRAMES_THRESHOLD

class SilenceDetector:
    def __init__(self):
        self.vad = SileroVAD(sample_rate=RATE)
        self.speech_done = threading.Event()
        self.state = {'is_speaking': False, 'silence_count': 0}
    
    def process_chunk(self, chunk):
        # Convert int16 to float32 in range [-1, 1]
        audio_float32 = chunk.flatten().astype(np.float32) / 32768.0
        prob = self.vad.process(audio_float32)

        # Update speech state based on VAD probability
        if prob > VAD_THRESHOLD:
            self.state['is_speaking'] = True
            self.state['silence_count'] = 0
        elif self.state['is_speaking']:
            self.state['silence_count'] += 1

        # Detect end of speech after sustained silence
        if self.state['is_speaking'] and self.state['silence_count'] > VAD_SILENCE_FRAMES_THRESHOLD:
            self.speech_done.set()

    def reset(self):
        self.state = {'is_speaking': False, 'silence_count': 0}
        self.speech_done.clear()

    def is_speech_done(self):
        return self.speech_done.is_set()