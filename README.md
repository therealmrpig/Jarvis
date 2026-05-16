# Jarvis: Local Intelligence System

A privacy-centric, low-latency AI assistant designed for high-performance execution on local hardware. Engineered for edge devices, prioritizing efficiency and data sovereignty over conversational filler.

## Core Directives
- **Local-First:** All processing (STT, LLM, TTS, Wake Word) occurs on-device. No data leaves the local network.
- **Privacy by Design:** Zero cloud dependencies except for tooling. No telemetry.
- **Efficiency:** Low-latency execution optimized for legacy hardware.

## Components

Jarvis leverages a modular architecture of local tools:

- **Wake Word Detection:** [OpenWakeWord](https://github.com/dscripka/openWakeWord) for efficient, low-latency trigger word monitoring.
- **Speech-to-Text (STT):** [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) for near real-time, high-accuracy transcriptions.
- **Language Model (LLM):** [Ollama](https://ollama.com/) running **Gemma 4** for sophisticated reasoning and technical assistance.
- **Text-to-Speech (TTS):** [Piper](https://github.com/rhasspy/piper) for natural-sounding, low-latency speech synthesis.

## Roadmap: Engineering Goals
- **MemPalace:** Implementation of a SQLite-based vector store for long-term hierarchical memory.
- **Functional Routing:** Intent classification using lightweight models to bypass the main LLM for system-level tasks.
- **Computer Control:** Tool-calling capabilities for direct filesystem and application interaction.
- **Agent instructing:** Ability to prompt harnesses like Claude Code, gemini-cli, Pi, and OpenCode.

---
*Status: Active Development.*
