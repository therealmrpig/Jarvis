import pyaudio
import numpy as np
from openwakeword.model import Model

model = Model(inference_framework="onnx", wakeword_models=["OpenWakeword-Modelfiles/jarvis-v2.onnx"])

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280

audio = pyaudio.PyAudio()
mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                        input=True, frames_per_buffer=CHUNK)

print("\n--- Listening for Wakewords ---")
print(f"Loaded models: {list(model.models.keys())}\n")


try:
    while True:
        data = mic_stream.read(CHUNK, exception_on_overflow=False)
        audio_frame = np.frombuffer(data, dtype=np.int16)

        prediction = model.predict(audio_frame)

        for mdl, score in prediction.items():
            if score > 0.5:
                print(f"DETECTED: {mdl} (Score: {score:.4f})")

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    mic_stream.stop_stream()
    mic_stream.close()
    audio.terminate()