from faster_whisper import WhisperModel
from jarvis.config import STT_MODEL, STT_DEVICE, STT_COMPUTE_TYPE, STT_LANGUAGE

class SpeechToText:
    def __init__(self):
        self.model = WhisperModel(STT_MODEL, device=STT_DEVICE, compute_type=STT_COMPUTE_TYPE, local_files_only=True)
    
    def transcribe(self, audio_float32):
        segments, _ = self.model.transcribe(audio_float32, language=STT_LANGUAGE)
        return " ".join([seg.text for seg in segments])