import queue
import threading
import sounddevice as sd
from piper import PiperVoice, SynthesisConfig
from jarvis.config import (
    TTS_VOICE_MODEL,
    TTS_VOLUME,
    TTS_LENGTH_SCALE,
    TTS_NOISE_SCALE,
    TTS_NOISE_W_SCALE,
    TTS_NORMALIZE_AUDIO,
    MIN_SENTENCE_LENGTH
)


class TextToSpeech:
    def __init__(self):
        # Create the audio synthesis config with all the voice settings from config.py
        self.syn_config = SynthesisConfig(
            volume=TTS_VOLUME,
            length_scale=TTS_LENGTH_SCALE,
            noise_scale=TTS_NOISE_SCALE,
            noise_w_scale=TTS_NOISE_W_SCALE,
            normalize_audio=TTS_NORMALIZE_AUDIO,
        )
        # Load the Piper voice model from disk
        self.voice = PiperVoice.load(TTS_VOICE_MODEL)

        # Create two queues:
        # - text_queue: Main loop puts sentences here, synthesis worker takes from here
        # - audio_queue: Synthesis worker puts audio chunks here, playback worker takes from here
        self.text_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._is_playing = threading.Event()

        # Start two background threads that run forever
        # daemon=True means they stop when main program exits
        threading.Thread(target=self._synthesis_worker, daemon=True).start()
        threading.Thread(target=self._playback_worker, daemon=True).start()

    def is_busy(self):
        # Returns True if there is text to synthesize, audio to play, or playback is active
        return not self.text_queue.empty() or not self.audio_queue.empty() or self._is_playing.is_set()

    def wait(self):
        self.text_queue.join()
        self.audio_queue.join()

    def _synthesis_worker(self):
        # This thread runs in the background and continuously processes text
        while True:
            # Get text from the queue (blocks if queue is empty)
            text = self.text_queue.get()
            
            # If we get None, it means shutdown was called, so exit this loop
            if text is None:
                break

            # Remove asterisks from text (markdown formatting like **bold**)
            text = text.replace('*', '')

            # Convert text to audio using the Piper voice model
            # This returns audio chunks, so we loop through each one
            for audio_chunk in self.voice.synthesize(text, syn_config=self.syn_config):
                if self._stop_event.is_set():
                    break
                # Put each audio chunk into the audio queue for playback
                self.audio_queue.put(audio_chunk.audio_int16_array)

            # Tell the queue we finished processing this text
            self.text_queue.task_done()

    def _playback_worker(self):
        # This thread runs in the background and plays audio continuously
        while True:
            # Get an audio chunk from the queue (blocks if queue is empty)
            chunk = self.audio_queue.get()
            
            # If we get None, it means shutdown was called, so exit this loop
            if chunk is None:
                break

            if self._stop_event.is_set():
                self.audio_queue.task_done()
                continue

            # Play the audio chunk using sounddevice at the correct sample rate
            self._is_playing.set()
            print('[DEBUG] set event')
            sd.play(chunk, samplerate=self.voice.config.sample_rate)
            # Wait for the audio to finish playing before getting the next chunk
            sd.wait()
            self._is_playing.clear()
            print('[DEBUG] cleared event')

            # Tell the queue we finished processing this audio chunk
            self.audio_queue.task_done()

    def synthesize(self, text):
        # Called from main loop when a complete sentence is detected
        # This puts the sentence into the text queue for the synthesis worker to process
        text = text.strip()
        # Only queue sentences that have meaningful length
        if len(text) > MIN_SENTENCE_LENGTH:
            self._stop_event.clear()
            self.text_queue.put(text)

    def halt(self):
        self._stop_event.set()
        self._is_playing.clear()
        print('[DEBUG] cleared event')
        sd.stop()
        while not self.text_queue.empty():
            try:
                self.text_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
