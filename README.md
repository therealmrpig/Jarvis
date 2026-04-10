# Jarvis: Local Intelligence System

A privacy-centric, low-latency AI assistant designed for high-performance execution on local hardware. Engineered for a 2015 Mac (Intel CPU), prioritizing efficiency and data sovereignty over conversational filler.

## Core Directives
- **Local-First:** All processing (STT, LLM, TTS, Wake Word) occurs on-device. No data leaves the local network.
- **Privacy by Design:** Zero cloud dependencies. No telemetry. 
- **Efficiency:** Low-latency execution optimized for legacy hardware.

## Technical Architecture

### Component Stack
- **Wake Word Detection:** OpenWakeWord (ONNX-optimized) for low-overhead background monitoring.
- **Speech-to-Text (STT):** Faster-Whisper (Tiny/Base models) utilizing CTranslate2 for efficient CPU inference.
- **Inference Engine:** Ollama (Gemma 2 / Llama 3.2) for localized language modeling.
- **Text-to-Speech (TTS):** Piper (ONNX) for fast, natural-sounding synthesis without GPU requirements.

### Current Pipeline
1. **Listen:** Continuous buffer monitoring for the `jarvis` wake word.
2. **Capture:** VAD-triggered recording with dynamic silence detection.
3. **Transcribe:** Local inference via Faster-Whisper.
4. **Think:** Context-aware response generation via Ollama.
5. **Synthesize:** Sentence-buffered streaming TTS for perceived zero-latency response.

## Installation & Deployment

### Environment Setup
The system is designed to run in a isolated Python virtual environment.

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
