import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
from ollama import chat
import select

SAMPLE_RATE = 16000
MODEL_KEEP_ALIVE = "5m"  # Keep Ollama model loaded

# Load Whisper once
whisper_model = WhisperModel("tiny", device="cpu")  # use "cuda" if you have GPU

# Chat history for context
chat_history = []

# ---------------- Helper Functions ---------------- #

def input_ready():
    import sys
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def record_audio():
    print("Recording... Press Enter again to stop.")
    recording = []
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    stream.start()
    try:
        while True:
            data, _ = stream.read(1024)
            recording.append(data)

            if input_ready():
                input()  # consume Enter
                break
    finally:
        stream.stop()
        stream.close()

    audio = np.concatenate(recording, axis=0)
    return audio


def transcribe(audio):
    wav.write("temp.wav", SAMPLE_RATE, audio)
    segments, _ = whisper_model.transcribe("temp.wav", beam_size=1, best_of=1)
    return " ".join([seg.text for seg in segments])


def stream_ollama(user_text):
    """
    Stream response from your custom Ollama model while keeping context.
    """
    global chat_history
    # Append user message
    chat_history.append({"role": "user", "content": user_text})

    # Stream response
    stream = chat(
        model="jarvis-gemma-v1",
        messages=chat_history,
        stream=True,
        keep_alive=MODEL_KEEP_ALIVE
    )

    reply = ""
    for chunk in stream:
        token = chunk["message"]["content"]
        print(token, end="", flush=True)
        reply += token
    print()  # newline at end

    # Append assistant reply to context
    chat_history.append({"role": "assistant", "content": reply})
    return reply

# ---------------- Main Loop ---------------- #

def main():
    print("Jarvis assistant ready! Press Enter to start recording commands.\n")

    while True:
        input("Press Enter to start recording...")

        audio = record_audio()
        text = transcribe(audio)

        print(f"\nYou said: {text}\n")
        print("Jarvis:", end=" ", flush=True)

        # Stream Ollama response while printing
        stream_ollama(text)
        print("\n" + "-" * 40 + "\n")


if __name__ == "__main__":
    main()
