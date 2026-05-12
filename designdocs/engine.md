# `jarvis/engine.py` Deep Dive

## Purpose
The `Engine` class is the orchestrator of the entire Jarvis system. it manages the lifecycle of all components, handles state transitions, and implements the complex logic for asynchronous barge-in.

## State Management: `JarvisState`
An `Enum` representing the four logical phases of the system:
1.  **`IDLE`**: Listening for the wake word.
2.  **`LISTENING`**: Recording user speech after a trigger.
3.  **`THINKING`**: Transcribing and generating a response.
4.  **`SPEAKING`**: Synthesizing and playing back the response.

## Class: `Engine`

### `__init__(self)`
*   **Component Instantiation:** Initializes STT, LLM, TTS, VAD, and **two** separate Wake Word detectors.
*   **Detector Strategy:** Two detectors (`activation_wakeword` and `bargein_wakeword`) are used to maintain separate internal RNN states, ensuring that the barge-in monitor doesn't interfere with the next idle-phase trigger.
*   **Queue Subscription:** Creates two dedicated audio queues from `AudioStream`.

### `async def startup(self)`
*   Starts the `AudioStream` producer.
*   Uses `asyncio.wait` to run `_main_loop` and `_monitor_interrupt` concurrently.
*   **Failure Handling:** If either task fails, it cancels the other and initiates a graceful shutdown.

### `async def _main_loop(self)`
This method implements the core conversation logic:
1.  **Wait for Wake Word:**
    *   State = `IDLE`.
    *   Clears all buffers.
    *   Reads chunks from `main_queue` and feeds them to `activation_wakeword.predict`.
    *   Uses a "rolling window" strategy (though simplified to direct chunks in the latest version for efficiency).
2.  **Record User Speech:**
    *   State = `LISTENING`.
    *   Resets `SilenceDetector`.
    *   Collects chunks until VAD detects sustained silence.
3.  **Process Request:**
    *   State = `THINKING`.
    *   Transcription via `SpeechToText`.
    *   Adds message to `LanguageModel`.
4.  **Execute & Speak:**
    *   State = `SPEAKING`.
    *   Starts streaming from LLM in a separate thread (via `asyncio.to_thread`) to prevent blocking.
    *   Buffers text into sentences.
    *   Sends sentences to `TextToSpeech` immediately.
    *   **Barge-In Check:** Periodically checks `self.interrupted.is_set()`. If true, it calls `tts.halt()` and breaks the loop to return to IDLE.

### `async def _monitor_interrupt(self)`
*   Runs continuously in the background.
*   Only performs inference when state is `SPEAKING` or `THINKING`.
*   **Barge-In Threshold:** Uses a higher threshold (`WAKEWORD_THRESHOLD + 0.2`) to avoid false triggers caused by Jarvis's own voice (acoustic echo).
*   If triggered, it sets `self.interrupted`, signaling the `_main_loop` to kill the current turn.

## Optimization & Robustness
*   **Concurrency:** Effectively manages multiple high-CPU background tasks without stuttering.
*   **Barge-In Sensitivity:** The separate detector and increased threshold provide a balance between "easy to interrupt" and "false interruptions."
*   **Graceful Termination:** Every loop checks `self.running`, ensuring immediate response to a shutdown signal.
