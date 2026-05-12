import numpy as np
import asyncio
from enum import Enum, auto

from jarvis.audio_stream import AudioStream
from jarvis.wake_word import WakeWordDetector
from jarvis.silence_detection import SilenceDetector
from jarvis.speech_to_text import SpeechToText
from jarvis.language_model import LanguageModel
from jarvis.text_to_speech import TextToSpeech
from jarvis.config import CHUNK, READ_SIZE_FOR_VAD, SENTENCE_TERMINATORS, WAKEWORD_THRESHOLD

class JarvisState(Enum):
    IDLE = auto()
    LISTENING = auto()
    THINKING = auto()
    SPEAKING = auto()

class Engine:
    def __init__(self):
        # Initialize all components
        self.audio_stream = AudioStream()
        self.stt = SpeechToText()
        self.llm = LanguageModel()
        self.activation_wakeword = WakeWordDetector()
        self.bargein_wakeword = WakeWordDetector()
        self.silence_detector = SilenceDetector()
        self.tts = TextToSpeech()

        self.running = False
        self.state = JarvisState.IDLE
        self.interrupted = asyncio.Event()

        # Subscribe to audio stream
        self.main_queue = self.audio_stream.get_new_queue()
        self.interrupt_queue = self.audio_stream.get_new_queue()

    async def startup(self):
        """Initializes the engine, starts audio capture, and runs the main loops concurrently."""
        self.running = True
        print("Jarvis ready!")

        # Start the audio producer
        await self.audio_stream.start_listening()

        # Run the main loop and interrupt monitor concurrently
        tasks = [
            asyncio.create_task(self._main_loop()),
            asyncio.create_task(self._monitor_interrupt())
        ]

        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            for task in pending:
                task.cancel()
            for task in done:
                if task.exception():
                    raise task.exception()
        finally:
            self.running = False
            for task in tasks:
                if not task.done():
                    task.cancel()

    async def _main_loop(self):
        """The core conversational loop of the engine."""
        while self.running:
            # 1. Listen for wakeword
            self.state = JarvisState.IDLE
            self.audio_stream.clear_queue(self.main_queue)
            self.audio_stream.clear_queue(self.interrupt_queue)
            self.activation_wakeword.clear_buffer()
            print("\nListening for wakeword...")

            while self.running:
                data = await self.main_queue.get()
                if data is None: break
                chunk = np.frombuffer(data, dtype=np.int16)

                # Pass chunk directly to stateful model
                predictions = await asyncio.to_thread(self.activation_wakeword.predict, chunk)
                is_triggered, model_name, score = self.activation_wakeword.is_triggered(predictions)

                if is_triggered:
                    print(f"DETECTED: {model_name} ACCURACY: {score:.4f}")
                    break

            if not self.running:
                break

            # 2. Record until silence
            self.state = JarvisState.LISTENING
            self.audio_stream.clear_queue(self.interrupt_queue)
            self.silence_detector.reset()
            stt_audio_data = []
            print("Recording...")

            while not self.silence_detector.is_speech_done() and self.running:
                data = await self.main_queue.get()
                if data is None: break
                chunk = np.frombuffer(data, dtype=np.int16)
                stt_audio_data.append(chunk)
                self.silence_detector.process_chunk(chunk)

            if not self.running:
                break

            # 3. Transcribe
            self.state = JarvisState.THINKING
            self.audio_stream.clear_queue(self.interrupt_queue)
            self.bargein_wakeword.clear_buffer()

            audio_float32 = np.concatenate(stt_audio_data, axis=0).astype(np.float32) / 32768.0
            transcription = await asyncio.to_thread(self.stt.transcribe, audio_float32)
            print("User: " + transcription)

            # 4. LLM response with TTS and Barge-In check
            self.llm.add_user_message(transcription)
            print("Jarvis: ", end="", flush=True)

            full_response = ""
            sentence_buffer = ""

            self.interrupted.clear()
            self.state = JarvisState.SPEAKING
            self.audio_stream.clear_queue(self.interrupt_queue)
            self.bargein_wakeword.clear_buffer()

            # Helper to iterate sync generator in a thread
            def get_stream():
                try:
                    return self.llm.chat_stream()
                except Exception as e:
                    print(f"LLM Error: {e}")
                    return []

            # Stream LLM chunks asynchronously
            llm_gen = await asyncio.to_thread(get_stream)

            while True:
                chunk = await asyncio.to_thread(next, llm_gen, None)
                if chunk is None or self.interrupted.is_set():
                    if self.interrupted.is_set():
                        print("\n[Interrupted during generation]")
                        self.tts.halt()
                    break

                print(chunk, end='', flush=True)
                full_response += chunk
                sentence_buffer += chunk

                if any(punct in chunk for punct in SENTENCE_TERMINATORS):
                    sentence = sentence_buffer.strip()
                    if len(sentence) > 1:
                        self.tts.synthesize_sentence(sentence)
                    sentence_buffer = ""

            if not self.interrupted.is_set():
                if sentence_buffer.strip():
                    self.tts.synthesize_sentence(sentence_buffer.strip())

                # Wait for TTS to finish unless interrupted
                while self.tts.is_busy() and not self.interrupted.is_set():
                    await asyncio.sleep(0.1)

                if self.interrupted.is_set():
                    print("\n[Interrupted during playback]")
                    self.tts.halt()

            self.llm.add_assistant_message(full_response)
            print()
            self.interrupted.clear()

    async def _monitor_interrupt(self):
        """Background task that monitors the microphone for the wake word while Jarvis is speaking."""
        while self.running:
            data = await self.interrupt_queue.get()
            if data is None: break

            # Only monitor for wake word when SPEAKING or THINKING
            if self.state in [JarvisState.SPEAKING, JarvisState.THINKING]:
                chunk = np.frombuffer(data, dtype=np.int16)

                # Pass chunk directly to stateful model
                predictions = await asyncio.to_thread(self.bargein_wakeword.predict, chunk)

                # Manual trigger check with higher threshold for barge-in
                for mdl, score in predictions.items():
                    if score > (WAKEWORD_THRESHOLD + 0.2):
                        print(f"\n[Barge-in detected: {score:.4f}]")
                        self.interrupted.set()
                        break

    async def shutdown(self):
        """Cleans up all components and stops the engine."""
        print("\nShutting down...")
        self.running = False
        if self.tts:
            self.tts.shutdown()
        if self.audio_stream:
            self.audio_stream.cleanup()