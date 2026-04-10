# Jarvis: Local AI Assistant

Jarvis is a high-performance, local-first intelligent assistant. Built with privacy and efficiency as core principles, it handles Speech-to-Text (STT), Language Modeling (LLM), and Text-to-Speech (TTS) entirely on your local machine.

---

## 🛠️ Philosophy

- **Local-First:** All processing happens on your hardware. No data ever leaves your network.
- **Intelligence over Politeness:** Designed for direct, efficient communication and deep technical assistance.
- **Modularity:** Each component (Audio, STT, LLM, TTS, Wake Word) is isolated for easy swapping and upgrades.
- **Persistent Memory:** Implements the MemPalace hierarchical memory architecture with AAAK shorthand for long-term context retention.

---

## 🚀 How to Use

### 1. Prerequisites
- **Python 3.10+**
- **Ollama** installed and running (for the LLM).
- **FFmpeg** (required by `faster_whisper`).
- A microphone and speakers for audio interaction.

### 2. Setup
1.  **Clone the repository:**
    ```bash
    git clone [repo-url]
    cd Jarvis
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv jarvisenv
    source jarvisenv/bin/activate  # On Windows: jarvisenv\Scripts\activate
    ```
3.  **Install dependencies:**
    *(Note: Ensure all required libraries like `numpy`, `faster_whisper`, `openwakeword`, `pyaudio`, and `ollama` are installed in your environment.)*

### 3. Execution
Start the assistant by running the main entry point:
```bash
python -m jarvis.main
```
Wait for the **"Jarvis ready!"** message, then say the wake word (default: "Jarvis") followed by your request.

---

## 🧠 How It Works

### 🎙️ Wake Word Detection
- **Technology:** [OpenWakeWord](https://github.com/dscripka/openWakeWord)
- **Model:** Pre-trained `.onnx` models (e.g., `jarvis-v2.onnx`).
- **Function:** Efficiently listens for the trigger word with minimal CPU usage.

### 👂 Speech-to-Text (STT)
- **Technology:** [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
- **Model:** `tiny.en` (configurable in `config.py`).
- **Function:** Converts your spoken audio into text transcription in near real-time.

### 🤖 Language Model (LLM)
- **Technology:** [Ollama](https://ollama.com/)
- **Model:** Custom `jarvis-gemma-v3` (modified Google Gemma 3).
- **Function:** Processes the transcription, reasons through the request, and generates a response. Supports context streaming for low-latency feedback.

### 🏠 Memory (MemPalace)
- **Architecture:** Hierarchical storage using **Wings**, **Rooms**, and **Halls**.
- **Compression:** Uses **AAAK shorthand** (Assertion, Assumption, Action, Knowledge) to compress months of history into a few hundred tokens.
- **Persistence:** Combines AAAK summaries (Closets) for speed and verbatim transcripts (Drawers) for accuracy.

### 🔊 Text-to-Speech (TTS)
- **Technology:** [Piper](https://github.com/rhasspy/piper)
- **Voice:** High-quality `jarvis-high.onnx` voice model.
- **Function:** Streams the LLM's response back to you as clear, natural-sounding audio.

---

## ⚙️ Configuration
All hardware-specific settings, model paths, and thresholds can be tuned in:
`jarvis/config.py`
