# General imports
import signal
import sys
import time

# STT imports
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

# LLM imports
from ollama import chat

# TTS imports
from piper import PiperVoice
from piper import SynthesisConfig
import queue

# Wake word imports
import pyaudio
from openwakeword.model import Model

# Voice detection imports
from silero_vad_lite import SileroVAD
import threading

# Audio stream handling
audio = pyaudio.PyAudio()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280

mic_stream = audio.open(
    format=FORMAT, 
    channels=CHANNELS, 
    rate=RATE, 
    input=True, 
    frames_per_buffer=CHUNK
)

# Graceful shutdown logic
def signal_handler(sig, frame):
    print("\nCleaning up Jarvis")
    text_queue.put(None)
    audio_queue.put(None)
    try:
        mic_stream.stop_stream()
        mic_stream.close()
        audio.terminate()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# STT variables
whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8", local_files_only=True)
stt_audio_data = []

# LLM variables
message_context = []

# TTS variables & audio player
syn_config = SynthesisConfig(
    volume=0.5,
    length_scale=1.0,
    noise_scale=1.0,
    noise_w_scale=1.0,
    normalize_audio=True,
)
voice = PiperVoice.load("Piper-Modelfiles/jarvis-high.onnx")

text_queue = queue.Queue()
audio_queue = queue.Queue()

def playback_worker():
    while True:
        chunk = audio_queue.get()
        if chunk is None: break
        sd.play(chunk, samplerate=voice.config.sample_rate)
        sd.wait()
        audio_queue.task_done()

def synthesis_worker():
    while True:
        text = text_queue.get()
        if text is None: break
        text = text.replace("*", "")

        # Generate audio chunks and pass them to the playback queue
        for audio_chunk in voice.synthesize(text, syn_config=syn_config):
            audio_queue.put(audio_chunk.audio_int16_array)
        
        text_queue.task_done()

threading.Thread(target=synthesis_worker, daemon=True).start()
threading.Thread(target=playback_worker, daemon=True).start()

# Wake word setup
oww_model = Model(inference_framework="onnx", wakeword_models=["OpenWakeword-Modelfiles/jarvis-v2.onnx"])
triggered = False

# Voice detecting setup
vad = SileroVAD(sample_rate=16000)
speech_done = threading.Event()

def monitor_silence(chunk, state):
    audio_float32 = chunk.flatten().astype(np.float32) / 32768.0
    prob = vad.process(audio_float32)

    if prob > 0.4:
        state['is_speaking'] = True
        state['silence_count'] = 0
    elif state['is_speaking']:
        state['silence_count'] += 1

    if state['is_speaking'] and state['silence_count'] > 15:
        speech_done.set()

while True:
    # -- Speech to text

    # Clear the stream & wakeword model buffer
    if mic_stream.get_read_available() > 0:
            mic_stream.read(mic_stream.get_read_available(), exception_on_overflow=False)
    
    for i in range(5):
        oww_model.predict(np.zeros(CHUNK, dtype=np.int16))
    
    print("\nListening for wakeword...")
    while not triggered:
        data = mic_stream.read(CHUNK, exception_on_overflow=False)
        audio_frame = np.frombuffer(data, dtype=np.int16)

        prediction = oww_model.predict(audio_frame)
        for mdl, score in prediction.items():
            if score > 0.5:
                print(f"DETECTED: {mdl} (Score: {score:.4f})")
                triggered = True

    # Clear audio buffer, silence flag & the vad state
    stt_audio_data.clear()
    speech_done.clear()
    vad_state = {'is_speaking': False, 'silence_count': 0}

    # Start stream
    while not speech_done.is_set():
        # We use a smaller read size for faster VAD response
        data = mic_stream.read(512, exception_on_overflow=False)
        chunk = np.frombuffer(data, dtype=np.int16)
        
        stt_audio_data.append(chunk)
        monitor_silence(chunk, vad_state)
    
    # Convert stream so whisper can read it
    audio_float32 = np.concatenate(stt_audio_data, axis=0).astype(np.float32) / 32768.0
    
    # Transcribe with fasterwhisper
    segments, _ = whisper_model.transcribe(audio_float32, language="en")
    transcription = " ".join([seg.text for seg in segments])

    print("User: " + transcription)

    # -- LLM

    # Append the transcription to the conversation context so the model remembers previous queries in the convo
    message_context.append({'role': 'user', 'content':transcription})

    # Start the model with streaming mode turned on, preventing ollama from waiting and delivering everything at once, and instead printing small chunks one by one
    stream = chat(
        model="jarvis-gemma-v3",
        messages=message_context,
        stream=True,
        keep_alive=-1,
        think=False
    )

    # Print the person indicator with end="" so Python doesnt start a new block on each chunk and flush=True so the terminal shows text immediately without Python buffering
    print("Jarvis: ", end="", flush=True)
    full_response = ""
    sentence_buffer = ""

    # Print the chunks one by one
    for chunk in stream:
        content = chunk['message']['content']
        print(content, end='', flush=True)
    
        full_response += content
        sentence_buffer += content

        if any(punct in content for punct in {'.', '!', '?', '\n'}):
            sentence = sentence_buffer.strip()
            if len(sentence) > 1:
                text_queue.put(sentence)
            sentence_buffer = ""

    # Catch any remaining text
    if sentence_buffer.strip():
        text_queue.put(sentence_buffer.strip())
    
    message_context.append({'role': 'assistant', 'content': full_response})
    print()
    text_queue.join()
    audio_queue.join()

    triggered = False
    print("resuming runner")
