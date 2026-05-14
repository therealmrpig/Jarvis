# `jarvis/text_to_speech.py` Deep Dive

## Purpose
The `TextToSpeech` class provides high-quality voice synthesis using the Piper ONNX engine. It is designed for low-latency, "interruptible" playback.

## Class: `TextToSpeech`

### Dual-Threaded Worker Architecture
To ensure zero-gap playback, TTS uses two dedicated background threads:

1.  **`_synthesis_worker`**:
    *   Consumes text from `text_queue`.
    *   Uses Piper to convert text to `int16` audio arrays.
    *   Piper yields chunks of audio, which are immediately pushed to the `audio_queue`.
    *   **Interruption:** Checks `self._stop_event` after every chunk to stop synthesis immediately if a barge-in occurs.

2.  **`_playback_worker`**:
    *   Consumes audio arrays from `audio_queue`.
    *   Plays them using `sounddevice`.
    *   **Playback Tracking:** Sets `self._is_playing = True` during `sd.play()` and `False` after `sd.wait()`. This allows the engine to know exactly when the audio has finished coming out of the speakers.

### `halt(self)`
This is the "Panic Button" for the Barge-In system.
1.  **Signal:** Sets `self._stop_event` to tell workers to abort current tasks.
2.  **Hardware Stop:** Calls `sd.stop()` to instantly silence the speakers.
3.  **Purge:** Empties both `text_queue` and `audio_queue` to ensure no stale sentences are played when the user starts speaking again.

### `synthesize_sentence(self, text)`
*   Called by the `Engine` as soon as a complete sentence is received from the LLM.
*   Filters out sentences shorter than `MIN_SENTENCE_LENGTH`.
*   Queues the text for the background synthesis worker.

## Optimization & Quality
*   **Pipelining:** Synthesis of sentence B happens while sentence A is playing. This hides the "cost" of synthesis.
*   **Formatting:** Strips markdown characters (like asterisks) before synthesis to prevent the voice from sounding robotic or confused by punctuation.
*   **Audio Quality:** Uses `int16` 22050Hz (standard for Piper) which provides clear, natural-sounding voice with minimal CPU overhead.
