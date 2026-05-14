# `jarvis/audio_stream.py` Deep Dive

## Purpose
The `AudioStream` class is the low-level hardware abstraction layer for microphone input. It was specifically redesigned during the "Async Barge-In" update to provide a multi-subscriber, non-blocking audio source.

## Class: `AudioStream`

### `__init__(self)`
*   **PyAudio Initialization:** Sets up the PyAudio engine.
*   **Microphone Stream:** Opens a hardware stream with the following parameters:
    *   `format`: `paInt16` (16-bit integer samples).
    *   `channels`: `1` (Mono).
    *   `rate`: `16000` Hz (Standard for most voice models).
    *   `frames_per_buffer`: `512` (Matches the VAD window size for zero-latency processing).
*   **Subscriber Management:** Initializes `self.queues`, a list of `asyncio.Queue` objects. This allows multiple parts of the brain (Main Loop and Barge-In Monitor) to receive the exact same audio stream without "fighting" for chunks.

### `async def _producer(self)`
This is the heart of the "Always-On" listening capability.
1.  **Non-Blocking Reads:** Uses `asyncio.to_thread` to call `self.mic_stream.read`. This is vital because PyAudio's `read` is a blocking C-call that would otherwise freeze the entire Jarvis event loop.
2.  **Broadcasting:** Every chunk (512 samples) read from the mic is immediately `put` into every registered subscriber queue.
3.  **Error Handling:** If the hardware stream overflows or errors, it logs the error but attempts to stay alive unless the system is shutting down.

### `async def start_listening(self)`
*   Sets the `self.listening` flag to `True`.
*   Spawns the `_producer` as a background task using `asyncio.create_task`.

### `def stop_listening(self)`
*   Sets `self.listening` to `False`.
*   Sends a `None` sentinel to all subscriber queues. This "wakes up" any tasks waiting on `queue.get()` so they can exit gracefully.

### `def get_new_queue(self) -> asyncio.Queue`
*   Creates a new `asyncio.Queue`.
*   Adds it to the subscriber list.
*   This is called by the `Engine` during initialization to create the `main_queue` and `interrupt_queue`.

### `def clear_queue(self, queue: asyncio.Queue)`
*   Surgically empties a specific queue. 
*   **Critical for Barge-In:** Used during state transitions (e.g., from Idle to Speaking) to ensure the monitor isn't processing "stale" audio from 10 seconds ago.

## Optimization & Efficiency
*   **Thread Delegation:** By moving hardware I/O to a separate thread via `asyncio.to_thread`, the main event loop is free to run complex logic and animations.
*   **Memory Efficiency:** Instead of duplicating audio buffers in memory, it passes references to the same bytes objects across queues.
*   **Zero-Copy VAD:** The chunk size of 512 exactly matches the SileroVAD requirement, meaning no slicing or re-buffering is needed for voice detection.
