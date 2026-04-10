import signal
import sys
import numpy as np

from jarvis.audio_stream import AudioStream
from jarvis.wake_word import WakeWordDetector
from jarvis.silence_detection import SilenceDetector
from jarvis.speech_to_text import SpeechToText
from jarvis.language_model import LanguageModel
from jarvis.text_to_speech import TextToSpeech
from jarvis.config import CHUNK, READ_SIZE_FOR_VAD, SENTENCE_TERMINATORS

audio_stream = None
tts = None


def signal_handler(sig, frame):
    global audio_stream, tts
    print("\nShutting down...")
    if tts:
        tts.shutdown()
    if audio_stream:
        audio_stream.cleanup()
    sys.exit(0)


def main():
    global audio_stream, tts
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize all components
    audio_stream = AudioStream()
    stt = SpeechToText()
    llm = LanguageModel()
    wakeword = WakeWordDetector()
    silence_detector = SilenceDetector()
    tts = TextToSpeech()
    
    print("Jarvis ready!")
    
    while True:
        # Listen for wakeword
        audio_stream.flush_buffer()
        wakeword.clear_buffer()
        print("\nListening for wakeword...")
        while True:
            data = audio_stream.read(CHUNK, exception_on_overflow=False)
            audio_frame = np.frombuffer(data, dtype=np.int16)
            is_triggered, model_name, score = wakeword.is_triggered(wakeword.predict(audio_frame))
            if is_triggered:
                print(f"DETECTED: {model_name} ACCURACY: {score:.4f}")
                break
        
        # Record until silence
        silence_detector.reset()
        stt_audio_data = []
        print("Recording...")
        while not silence_detector.is_speech_done():
            data = audio_stream.read(READ_SIZE_FOR_VAD, exception_on_overflow=False)
            chunk = np.frombuffer(data, dtype=np.int16)
            stt_audio_data.append(chunk)
            silence_detector.process_chunk(chunk)
        
        # Transcribe
        audio_float32 = np.concatenate(stt_audio_data, axis=0).astype(np.float32) / 32768.0
        transcription = stt.transcribe(audio_float32)
        print("User: " + transcription)
        
        # LLM response with TTS
        llm.add_user_message(transcription)
        print("Jarvis: ", end="", flush=True)
        
        full_response = ""
        sentence_buffer = ""
        for chunk in llm.chat_stream():
            print(chunk, end='', flush=True)
            full_response += chunk
            sentence_buffer += chunk
            
            if any(punct in chunk for punct in SENTENCE_TERMINATORS):
                sentence = sentence_buffer.strip()
                if len(sentence) > 1:
                    tts.synthesize_sentence(sentence)
                sentence_buffer = ""
        
        if sentence_buffer.strip():
            tts.synthesize_sentence(sentence_buffer.strip())
        
        llm.add_assistant_message(full_response)
        print()
        tts.wait_completion()


if __name__ == "__main__":
    main()
