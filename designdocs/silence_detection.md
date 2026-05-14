# `jarvis/silence_detection.py` Deep Dive

## Purpose
The `SilenceDetector` class provides Voice Activity Detection (VAD) to determine when a user has started and, more importantly, finished speaking. This prevents the system from "cutting off" the user mid-sentence or waiting indefinitely after they are done.

## Class: `SilenceDetector`

### `__init__(self)`
*   **SileroVAD:** Initializes the `SileroVAD` model. This is a state-of-the-art, lightweight neural network specifically trained to distinguish human speech from background noise.
*   **State Management:** Tracks `is_speaking` (boolean) and `silence_count` (integer).
*   **Thread Safety:** Uses `self.speech_done = threading.Event()` to provide a thread-safe way for the `Engine` to check if recording should stop.

### `process_chunk(self, chunk)`
This is called for every 512-sample audio chunk captured during the `LISTENING` phase.
1.  **Normalization:** Converts the raw `int16` audio data to `float32` in the range `[-1, 1]`. This is the format expected by the Silero model.
2.  **Probability Calculation:** Runs the chunk through the VAD model to get a speech probability score.
3.  **State Logic:**
    *   **Speech Detected:** If probability > `VAD_THRESHOLD` (e.g., 0.4), it sets `is_speaking = True` and resets the `silence_count`.
    *   **Silence Detected:** If the user was already speaking but the probability drops, it increments the `silence_count`.
4.  **Completion Trigger:** If `is_speaking` is true and `silence_count` exceeds `VAD_SILENCE_FRAMES_THRESHOLD` (e.g., 15 chunks or ~480ms), it sets the `speech_done` event.

### `reset(self)`
*   Clears the internal counters.
*   Resets the `speech_done` event.
*   Called by the `Engine` at the start of every `LISTENING` phase.

## Efficiency & Performance
*   **Latency:** By using a 512-sample window (32ms), the VAD reacts almost instantly to speech onset.
*   **CPU Usage:** The "Lite" version of SileroVAD is extremely efficient, consuming negligible CPU compared to the Wake Word or STT models.
*   **Robustness:** The use of a "silence buffer" (`silence_count`) ensures that natural pauses between words don't prematurely trigger the end of the recording.
