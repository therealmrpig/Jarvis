# Jarvis: Local Intelligence System

A privacy-centric, low-latency AI assistant designed for high-performance execution on local hardware. Engineered for a 2015 Mac (Intel CPU), prioritizing efficiency and data sovereignty over conversational filler.

## Core Directives
- **Local-First:** All processing (STT, LLM, TTS, Wake Word) occurs on-device. No data leaves the local network.
- **Privacy by Design:** Zero cloud dependencies. No telemetry. 
- **Efficiency:** Low-latency execution optimized for legacy hardware.

## 🛠️ The Stack

Jarvis leverages a modular architecture of best-in-class local tools:

- **Wake Word Detection:** [OpenWakeWord](https://github.com/dscripka/openWakeWord) for efficient, low-latency trigger word monitoring.
- **Speech-to-Text (STT):** [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) for near real-time, high-accuracy transcriptions.
- **Language Model (LLM):** [Ollama](https://ollama.com/) running **Gemma 2** for sophisticated reasoning and technical assistance.
- **Text-to-Speech (TTS):** [Piper](https://github.com/rhasspy/piper) for natural-sounding, low-latency speech synthesis.

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Ollama** installed and running.
- **FFmpeg** (for audio processing).

### Setup
1. **Clone & Enter:**
   ```bash
   git clone [repo-url]
   cd Jarvis
   ```
2. **Environment:**
   Jarvis uses a virtual environment located in `jarvisenv/`.
   ```bash
   source jarvisenv/bin/activate
   pip install -r requirements.txt
   ```
3. **Models:**
   Ensure your model files are placed in the appropriate directories as specified in `jarvis/config.py`:
   - `Ollama-Modelfiles/` (e.g., `jarvis-gemma-v3`)
   - `OpenWakeword-Modelfiles/` (e.g., `jarvis-v2.onnx`)
   - `Piper-Modelfiles/` (e.g., `jarvis-high.onnx`)

### Execution
Launch the Jarvis core from the project root:
```bash
# Initialize environment
python3 -m venv jarvisenv
source jarvisenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Model Assets
Ensure models are placed in the designated directories:
- `OpenWakeword-Modelfiles/`: `.onnx` models.
- `Piper-Modelfiles/`: `.onnx` and `.json` voice configurations.
- `Ollama`: Ensure the Ollama daemon is running with `jarvis-gemma-v3` or equivalent.

## Roadmap: Engineering Goals
- **Asynchronous Core:** Transition from serial execution to a non-blocking `asyncio` TaskGroup architecture.
- **MemPalace:** Implementation of a SQLite-based vector store for long-term hierarchical memory.
- **Functional Routing:** Intent classification using lightweight models to bypass the main LLM for system-level tasks.
- **Computer Control:** Tool-calling capabilities for direct filesystem and application interaction.

---
*Status: Active Development. Optimized for Intel CPU architectures.*
