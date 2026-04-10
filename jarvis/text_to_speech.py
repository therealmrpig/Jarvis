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
    ASTERISK_CHAR,
    MIN_SENTENCE_LENGTH,
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

        # Start two background threads that run forever
        # daemon=True means they stop when main program exits
        threading.Thread(target=self._synthesis_worker, daemon=True).start()
        threading.Thread(target=self._playback_worker, daemon=True).start()

    def _synthesis_worker(self):
        # This thread runs in the background and continuously processes text
        while True:
            # Get text from the queue (blocks if queue is empty)
            text = self.text_queue.get()
            
            # If we get None, it means shutdown was called, so exit this loop
            if text is None:
                break

            # Remove asterisks from text (markdown formatting like **bold**)
            text = text.replace(ASTERISK_CHAR, "")

            # Convert text to audio using the Piper voice model
            # This returns audio chunks, so we loop through each one
            for audio_chunk in self.voice.synthesize(text, syn_config=self.syn_config):
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

            # Play the audio chunk using sounddevice at the correct sample rate
            sd.play(chunk, samplerate=self.voice.config.sample_rate)
            # Wait for the audio to finish playing before getting the next chunk
            sd.wait()
            
            # Tell the queue we finished processing this audio chunk
            self.audio_queue.task_done()

    def synthesize_sentence(self, text):
        # Called from main loop when a complete sentence is detected
        # This puts the sentence into the text queue for the synthesis worker to process
        text = text.strip()
        # Only queue sentences that have meaningful length
        if len(text) > MIN_SENTENCE_LENGTH:
            self.text_queue.put(text)

    def wait_completion(self):
        # Block the main loop until all synthesis and playback is finished
        # text_queue.join() waits for all text to be processed
        self.text_queue.join()
        # audio_queue.join() waits for all audio to be played
        self.audio_queue.join()

    def shutdown(self):
        # Called when exiting (Ctrl+C or end of program)
        # Immediately stop any ongoing playback
        sd.stop()
        # Put None into both queues to signal workers to stop
        # This makes the while loops in both workers exit
        self.text_queue.put(None)
        self.audio_queue.put(None)