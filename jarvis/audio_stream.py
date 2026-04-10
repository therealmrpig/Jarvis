import pyaudio
from jarvis.config import FORMAT, CHANNELS, RATE, CHUNK

class AudioStream:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.mic_stream = self.audio.open(
            format=FORMAT, 
            channels=CHANNELS, 
            rate=RATE, 
            input=True, 
            frames_per_buffer=CHUNK
        )

    def read(self, frames=CHUNK, exception_on_overflow=False):
        return self.mic_stream.read(frames, exception_on_overflow=exception_on_overflow)

    def get_read_available(self):
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
        self.flush_buffer()
        self.close()
        self.terminate()