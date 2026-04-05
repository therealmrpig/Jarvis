import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000

# Load Whisper
model = WhisperModel("tiny", device="cpu")  # use "cuda" if you have GPU


def record_audio():
    print("Recording... Press Enter again to stop.")

    recording = []
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    stream.start()

    try:
        while True:
            data, _ = stream.read(1024)
            recording.append(data)

            # Check if Enter is pressed (non-blocking trick)
            if input_ready():
                input()  # consume Enter
                break

    finally:
        stream.stop()
        stream.close()

    audio = np.concatenate(recording, axis=0)
    return audio


def input_ready():
    import sys
    import select
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def transcribe(audio):
    wav.write("temp.wav", SAMPLE_RATE, audio)

    segments, _ = model.transcribe("temp.wav")
    return " ".join([seg.text for seg in segments])


def main():
    while True:
        input("Press Enter to start recording...")

        audio = record_audio()
        text = transcribe(audio)

        print("\nYou said:", text)
        print()


if __name__ == "__main__":
    main()
