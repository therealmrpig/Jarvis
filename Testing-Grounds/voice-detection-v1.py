import numpy as np
import sounddevice as sd
from silero_vad_lite import SileroVAD

# Initialize VAD (16000Hz is standard for Jarvis/Whisper)
vad = SileroVAD(16000)

# VAD Lite requires exactly 512 samples for 16kHz (32ms of audio)
CHUNK_SIZE = 512 

def callback(indata, frames, time, status):
    # Convert to float32 and normalize to [-1.0, 1.0]
    audio_float32 = indata.flatten().astype(np.float32) / 32768.0
    
    # Get speech probability (0.0 to 1.0)
    prob = vad.process(audio_float32)
    
    # Visual feedback: Simple bar that grows with probability
    bar = "█" * int(prob * 20)
    print(f"\r[{bar:<20}] {prob:.2f} {'SPEECH' if prob > 0.5 else ''}", end="", flush=True)

print("Testing VAD... Speak into your mic! (Ctrl+C to stop)")

with sd.InputStream(samplerate=16000, channels=1, dtype='int16', 
                    blocksize=CHUNK_SIZE, callback=callback):
    try:
        while True:
            sd.sleep(100)
    except KeyboardInterrupt:
        print("\nTest stopped.")