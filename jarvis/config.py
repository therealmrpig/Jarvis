# Audio settings
import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280
READ_SIZE_FOR_VAD = 512

# STT (Speech-to-Text) settings
STT_MODEL = "tiny"
STT_DEVICE = "cpu"
STT_COMPUTE_TYPE = "int8"
STT_LANGUAGE = "en"

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

# Text processing settings
ASTERISK_CHAR = "*"
SENTENCE_TERMINATORS = {'.', '!', '?', '\n'}
MIN_SENTENCE_LENGTH = 1