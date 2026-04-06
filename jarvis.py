# STT imports
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel

# LLM imports
from ollama import chat

# TTS imports
from piper import PiperVoice
from piper import SynthesisConfig

# Wake word imports
import threading
from precise_runner import PreciseEngine, PreciseRunner
import speech_recognition as sr

# STT variables & functions
whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8", local_files_only=True)
stt_audio_data = []

def audio_callback(indata, frames, time, status):
    stt_audio_data.append(indata.copy())

# LLM variables
message_context = []

# TTS variables
syn_config = SynthesisConfig(
    volume=0.5,
    length_scale=0.8,
    noise_scale=0.667,
    noise_w_scale=0.8,
    normalize_audio=True,
)
voice = PiperVoice.load("Piper-Modelfiles/en_GB-alan-low.onnx")
tts_audio_data = []

# -- Wake word logic & setup
wake_word_triggered = threading.Event()

def wakeword_detected():
    print("wake word detected")
    wake_word_triggered.set()
def check_prob(prob):
    if prob > 0.01:
        print(f"Confidence: {prob:.2f}")

wake_word_mic = sr.Microphone(device_index=3, sample_rate=16000)

engine = PreciseEngine("/Users/melle/Projects/mycroft-precise/.venv/bin/precise-engine", "Precise-Modelfiles/jarvis.pb")
runner = PreciseRunner(engine, sensitivity=0.9, trigger_level=3, on_activation=wakeword_detected, on_prediction=check_prob, stream=wake_word_mic.stream)
runner.start()

while True:
    # -- Speech to text
    
    # Wait for wake word
    wake_word_triggered.wait()

    # Clear audio buffer
    stt_audio_data.clear()

    # Start stream
    stream = sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=audio_callback)
    stream.start()
    
    # End stream once input is given
    input("Recording... Press Enter to stop.") 
    
    stream.stop()
    stream.close()
    
    # Write stream to wav
    wav.write("input.wav", 16000, np.concatenate(stt_audio_data, axis=0))
    
    # Transcribe with fasterwhisper
    segments, _ = whisper_model.transcribe("input.wav")
    transcription = " ".join([seg.text for seg in segments])

    print("User: " + transcription)

    # -- LLM

    # Append the transcription to the conversation context so the model remembers previous queries in the convo
    message_context.append({'role': 'user', 'content':transcription})

    # Start the model with streaming mode turned on, preventing ollama from waiting and delivering everything at once, and instead printing small chunks one by one
    stream = chat(
        model="jarvis-gemma-v2",
        messages=message_context,
        stream=True,
        keep_alive=-1
    )

    # Print the person indicator with end="" so Python doesnt start a new block on each chunk and flush=True so the terminal shows text immediately without Python buffering
    print("Jarvis: ", end="", flush=True)
    full_response = ""

    # Print the chunks one by one
    for chunk in stream:
        content = chunk['message']['content']
        print(content, end='', flush=True)
        # Quietly build the full response for appending to context
        full_response += content
    
    # Append the response to the context
    message_context.append({'role': 'assistant', 'content': full_response})
    print()

    # -- Text to speech

    tts_audio_data.clear()
    
    for chunk_data in voice.synthesize(full_response, syn_config=syn_config):
        # Convert raw bytes to 16-bit integers (PCM)
        tts_audio_data.append(chunk_data.audio_int16_array)
    
    # Combine all chunks inside of one array
    full_tts_audio = np.concatenate(tts_audio_data)

    # Play audio and wait until finished before clearing the trigger, resuming the wait for the wake word detector
    sd.play(full_tts_audio, samplerate=voice.config.sample_rate)
    sd.wait()
    wake_word_triggered.clear()
    print("resuming runner")


    