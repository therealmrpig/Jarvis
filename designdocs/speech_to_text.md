# `jarvis/speech_to_text.py` Deep Dive

## Purpose
The `SpeechToText` class handles the conversion of raw audio data into text using the Faster-Whisper library. It is optimized for local execution and low latency.

## Class: `SpeechToText`

### `__init__(self)`
*   **WhisperModel Initialization:** Loads the Whisper model (e.g., "tiny", "base") onto the specified device (CPU or GPU).
*   **Quantization:** Uses `compute_type="int8"` by default. This significantly reduces memory usage and increases inference speed on CPUs without a noticeable drop in transcription accuracy for common assistant commands.
*   **`local_files_only=True`**: Ensures the system never attempts to download models from the internet during runtime, adhering to the "Local-First" constitutional mandate.

### `transcribe(self, audio_float32) -> str`
1.  **Input:** Accepts a 1D numpy array of `float32` audio samples.
2.  **Inference:** Calls `self.model.transcribe`.
    *   `language="en"`: Hardcoded to English to reduce language-detection latency.
    *   `beam_size=5`: A balance between accuracy and speed.
    *   `vad_filter=True`: An internal secondary VAD pass to ensure it only transcribes segments with actual speech.
3.  **Output:** Concatenates the text from all detected segments into a single string and returns it.

## Architectural Trade-offs
*   **Model Selection:** The "tiny" model is used for maximum speed. While "large-v3" is more accurate, the 2-5 second delay on local hardware is often unacceptable for a conversational assistant.
*   **Blocking Call:** Transcription is a heavy CPU/GPU task. In `engine.py`, this method is always called via `asyncio.to_thread` to ensure the rest of the system (like the Barge-In monitor) remains responsive while the model is calculating.

## Optimization Notes
*   **Memory:** The `int8` quantization allows the model to fit into ~150MB of RAM.
*   **Parallelism:** Faster-Whisper can utilize multiple CPU cores for the transcription process.
