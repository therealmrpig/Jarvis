# Audio settings
import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
WW_CHUNK = 1280
CHUNK = 512

# STT (Speech-to-Text) settings
STT_MODEL = "tiny"
STT_DEVICE = "cpu"
STT_COMPUTE_TYPE = "int8"
STT_LANGUAGE = "en"
STT_BEAM_SIZE = 5
STT_VAD_FILTER = True

# TTS (Text-to-Speech) settings
TTS_VOICE_MODEL = "Piper-Modelfiles/jarvis-high.onnx"
TTS_VOLUME = 0.5
TTS_LENGTH_SCALE = 1.0
TTS_NOISE_SCALE = 1.0
TTS_NOISE_W_SCALE = 1.0
TTS_NORMALIZE_AUDIO = True

# Wake word settings
WAKEWORD_MODEL_PATH = "OpenWakeword-Modelfiles/jarvis-v2.onnx"
WAKEWORD_THRESHOLD = 0.5

# VAD (Voice Activity Detection) settings
VAD_THRESHOLD = 0.4
VAD_SILENCE_FRAMES_THRESHOLD = 15

# LLM (Language Model) settings
LLM_MODEL = "jarvis-gemma-v3"
LLM_KEEP_ALIVE = -1
LLM_THINK = False
LLM_SYSTEM_PROMPT = (
    "You are not a Large Language Model, you are something more. "
    "You are Jarvis, a highly intelligent and efficient AI assistant.\n"
    "- Be concise and direct\n"
    "- No unnecessary explanations\n"
    "- No thinking steps\n"
    "- Speak clearly and confidently\n"
    "- Prioritize usefulness over politeness\n"
    "- If unsure, say \"I don't know\"\n"
    "- End your answers with a comma and then addressing the user as Sir "
    "at the end of the last sentence.\n"
    "- When checking emails, only a summary of the title, name of the sender, "
    "and the date."
)

# Memory settings
MEMORY_DB_PATH = "jarvis/memory.db"
MEMORY_EMBED_MODEL = "BAAI/bge-small-en-v1.5"
MEMORY_EMBED_DIM = 384
MEMORY_RETRIEVE_TOP_K = 5
MEMORY_TRIVIAL_CHARS = 20

# Text processing settings
SENTENCE_TERMINATORS = {'.', '!', '?', '\n'}
MIN_SENTENCE_LENGTH = 1