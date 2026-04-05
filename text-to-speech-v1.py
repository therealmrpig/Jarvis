import wave
from piper import PiperVoice
from piper import SynthesisConfig

syn_config = SynthesisConfig(
    volume=0.5,
    length_scale=1.0,
    noise_scale=1.0,
    noise_w_scale=1.0,
    normalize_audio=True,
)

voice = PiperVoice.load("Piper-Modelfiles/jarvis-high.onnx")
with wave.open("output.wav", "wb") as wav_file:
    voice.synthesize_wav("Welcome to the world of speech synthesis! I am the voice of your new assistant, Jarvis!", wav_file, syn_config=syn_config)
