# `jarvis/__main__.py` Deep Dive

## Purpose
The `__main__.py` file serves as the entry point for the Jarvis application. Its primary responsibility is to bootstrap the asynchronous event loop, initialize the `Engine`, and ensure a graceful shutdown when the user terminates the program.

## Logic Breakdown

### 1. Imports
*   `signal`: Used to handle operating system signals like `SIGINT` (Ctrl+C).
*   `sys`: Standard system library.
*   `asyncio`: The core library used to manage the asynchronous event loop.
*   `jarvis.engine.Engine`: The main orchestrator of the system.

### 2. `async def main()`
This is the core asynchronous entry point.
1.  **Engine Initialization:** Creates an instance of the `Engine` class.
2.  **Signal Handling:**
    *   Retrieves the currently running event loop.
    *   Attaches signal handlers for `SIGINT` (Interrupt) and `SIGTERM` (Termination).
    *   When these signals are received, it schedules the `engine.shutdown()` coroutine to run, ensuring all hardware (mic, speakers) and background threads are cleaned up before exit.
3.  **Startup:** Calls `await engine.startup()`, which hands control over to the `Engine` to start the main loops.
4.  **Cleanup (Finally):** The `finally` block ensures that even if an unhandled exception occurs, `engine.shutdown()` is called as a last resort.

### 3. Execution Guard
```python
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```
*   Uses `asyncio.run()` to start the top-level entry point.
*   Catches `KeyboardInterrupt` to suppress the messy Traceback when a user hits Ctrl+C.

## Design Considerations
*   **Async Native:** By using `asyncio.run` at the top level, the entire application context is asynchronous from the start.
*   **Graceful Exit:** The use of signal handlers is critical for local hardware applications. Without them, the microphone stream or speakers might remain "locked" by the OS even after the script ends.
