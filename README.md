# Jarvis: Your Local AI Sentinel

Jarvis is a high-performance, private, and local-first AI assistant. Built for the privacy-conscious enthusiast, Jarvis handles every stage of the intelligence pipeline—from wake-word detection to speech synthesis—entirely on your own hardware. No cloud, no telemetry, no compromises.

## 🛡️ Core Mandates

- **Local-First:** All processing (STT, TTS, LLM, Wake Word) is executed on the local machine.
- **Privacy by Design:** Your data and audio never leave your local network.
- **Intelligence over Politeness:** Designed to be direct, efficient, and technically precise.

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
python -m jarvis
```
Wait for the **"Jarvis ready!"** message, then speak the wake word followed by your command.

## 🗺️ Roadmap

We are constantly refining Jarvis to be the ultimate local assistant. Our current focus includes:

- [ ] **FunctionGemma Integration:** Implementing a lightweight routing model (FunctionGemma 270M) for optimized intent handling.
- [ ] **MemPalace Implementation:** Building the long-term hierarchical memory system with AAAK shorthand for superior context compression.
- [ ] **RAG Capabilities:** Adding Retrieval-Augmented Generation for local file context.
- [ ] **DevOps Pipeline:** GitHub Actions for automated linting and unit testing.

## ⚙️ Configuration
All hardware-specific settings, model paths, and sensitivity thresholds are managed in `jarvis/config.py`.

---
*Built for privacy. Powered by your hardware.*
