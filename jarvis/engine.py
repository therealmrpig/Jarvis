import numpy as np

from jarvis.audio_stream import AudioStream
from jarvis.wake_word import WakeWordDetector
from jarvis.silence_detection import SilenceDetector
from jarvis.speech_to_text import SpeechToText
from jarvis.language_model import LanguageModel
from jarvis.text_to_speech import TextToSpeech
from jarvis.config import CHUNK, READ_SIZE_FOR_VAD, SENTENCE_TERMINATORS

class Engine:
    def __init__(self):
        # Initialize all components
        self.audio_stream = AudioStream()
        self.stt = SpeechToText()
        self.llm = LanguageModel()
        self.wakeword = WakeWordDetector()
        self.silence_detector = SilenceDetector()
        self.tts = TextToSpeech()

        self.running = False
    
    def startup(self):
        self.running = True
        print("Jarvis ready!")
        
        while self.running:
            # Listen for wakeword
            self.audio_stream.flush_buffer()
            self.wakeword.clear_buffer()
            print("\nListening for wakeword...")
            while self.running:
                data = self.audio_stream.read(CHUNK, exception_on_overflow=False)
                audio_frame = np.frombuffer(data, dtype=np.int16)
                is_triggered, model_name, score = self.wakeword.is_triggered(self.wakeword.predict(audio_frame))
                if is_triggered:
                    print(f"DETECTED: {model_name} ACCURACY: {score:.4f}")
                    break
            
            # Record until silence
            self.silence_detector.reset()
            stt_audio_data = []
            print("Recording...")
            while not self.silence_detector.is_speech_done():
                data = self.audio_stream.read(READ_SIZE_FOR_VAD, exception_on_overflow=False)
                chunk = np.frombuffer(data, dtype=np.int16)
                stt_audio_data.append(chunk)
                self.silence_detector.process_chunk(chunk)
            
            # Transcribe
            audio_float32 = np.concatenate(stt_audio_data, axis=0).astype(np.float32) / 32768.0
            transcription = self.stt.transcribe(audio_float32)
            print("User: " + transcription)

            # LLM response with TTS
            self.llm.add_user_message(transcription)
            print("Jarvis: ", end="", flush=True)
            
            full_response = ""
            sentence_buffer = ""
            for chunk in self.llm.chat_stream():
                print(chunk, end='', flush=True)
                full_response += chunk
                sentence_buffer += chunk
                
                if any(punct in chunk for punct in SENTENCE_TERMINATORS):
                    sentence = sentence_buffer.strip()
                    if len(sentence) > 1:
                        self.tts.synthesize_sentence(sentence)
                    sentence_buffer = ""
            
            if sentence_buffer.strip():
                self.tts.synthesize_sentence(sentence_buffer.strip())
            
            self.llm.add_assistant_message(full_response)
            print()
            self.tts.wait_completion()

        def shutdown(self):
            print("\nShutting down...")
            if self.tts:
                self.tts.shutdown()
            if self.audio_stream:
                self.audio_stream.cleanup()
