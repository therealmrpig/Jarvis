# `jarvis/wake_word.py` Deep Dive

## Purpose
The `WakeWordDetector` class is a wrapper for the `openWakeWord` library. It provides "Always-On" keyword detection (e.g., "Jarvis") with extremely low power consumption.

## Class: `WakeWordDetector`

### `__init__(self)`
*   **Inference Engine:** Uses `onnxruntime` for the backend, which is highly optimized for both Intel and Apple Silicon CPUs.
*   **Model Loading:** Loads the specific `.onnx` model file defined in `config.py`.

### `predict(self, audio_frame) -> dict`
*   **Input:** Accepts a 1280-sample (80ms) audio frame.
*   **Stateful Inference:** The model is stateful (using a Recurrent Neural Network). Each call to `predict` updates the internal state based on the new audio, allowing it to "remember" the start of a word while listening to the end.
*   **Output:** Returns a dictionary of model names and their corresponding confidence scores (0.0 to 1.0).

### `is_triggered(self, predictions) -> (bool, str, float)`
*   Helper method that iterates through the prediction dictionary.
*   Compares the highest score against the `WAKEWORD_THRESHOLD`.
*   Returns a boolean flag along with the detected model name and accuracy score.

### `clear_buffer(self)`
*   **Echo Cancellation Simulation:** Feeds several chunks of "silence" (zeroed-out arrays) into the model.
*   **Reasoning:** This effectively "flushes" the internal RNN state. It is used after Jarvis finishes speaking to ensure that any "echo" of his own name heard by the microphone doesn't trigger a false barge-in for the next interaction.

## Optimization & Efficiency
*   **CPU Usage:** `openWakeWord` is designed to run on a single core with < 5% CPU usage.
*   **Latency:** The model processes audio in 80ms increments, providing nearly instantaneous detection.
*   **False Positive Protection:** In `engine.py`, two separate instances of this class are used to ensure the "Idle" detector and "Barge-In" detector never share or corrupt each other's hidden states.
