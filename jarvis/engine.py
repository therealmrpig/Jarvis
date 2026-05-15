import numpy as np
import asyncio

from jarvis.audio import Audio
from jarvis.wake_word import WakeWordMonitor
from jarvis.silence_detection import SilenceDetector
from jarvis.speech_to_text import SpeechToText
from jarvis.language_model import LanguageModel
from jarvis.text_to_speech import TextToSpeech
from jarvis.tools import registry
from jarvis.config import SENTENCE_TERMINATORS

class Engine:
    def __init__(self):
        self.audio = Audio()
        self.main_q = self.audio.subscribe()
        self.ww_q = self.audio.subscribe()
        self.wake_word_monitor = WakeWordMonitor(self.ww_q)

        self.vad = SilenceDetector()
        self.stt = SpeechToText()
        self.llm = LanguageModel()
        self.tts = TextToSpeech()

        self._running = False

    async def _respond(self, text):
        self.llm.add_user_message(text)
        self.wake_word_monitor.clear() # Clear wake word event for barge-in

        full_response = ''
        sentence_buffer = ''

        stream = self.llm.stream(tools=registry.get_definitions())

        while self._running:
            if self.wake_word_monitor.triggered.is_set():
                self.tts.halt()
                print('\n[Interrupted]')
                break

            chunk = await asyncio.to_thread(next, stream, None)
            if chunk is None:
                break

            if 'content' in chunk:
                c = chunk['content']
                print(c, end='', flush=True)
                full_response += c
                sentence_buffer += c

                if any(p in c for p in SENTENCE_TERMINATORS) and sentence_buffer.strip():
                    self.tts.synthesize(sentence_buffer.strip())
                    sentence_buffer = ''
            
            if 'tool_calls' in chunk:
                calls = chunk['tool_calls']
                self.llm.add_assistant_message(full_response, tool_calls=calls)
                for tc in calls:
                    print(f'\n[Tool] {tc.function.name}({tc.function.arguments})')
                    result = registry.execute(tc.function.name, tc.function.arguments)
                    self.llm.add_tool_message(result)
                full_response = ''
                sentence_buffer = ''
                stream = self.llm.stream(tools=registry.get_definitions())

        if not self.wake_word_monitor.triggered.is_set():
            if sentence_buffer.strip():
                self.tts.synthesize(sentence_buffer.strip())
            while self.tts.is_busy():
                if self.wake_word_monitor.triggered.is_set():
                    self.tts.halt()
                    print('\n[Interrupted]')
                    self.wake_word_monitor.clear() # Clear wake word event for barge-in
                    return
                await asyncio.sleep(0.1)
            self.llm.add_assistant_message(full_response)
    
    async def start(self):
        self._running = True

        # Initialize audio & wake word monitor
        await self.audio.start()
        asyncio.create_task(self.wake_word_monitor.start())

        while self._running:

            # ---- Wake word ----
            self.wake_word_monitor.clear()
            print('\nListening...')

            await self.wake_word_monitor.triggered.wait()
            if not self._running:
                break

            
            # ---- Silence Detection ----
            print('Wake word detected! Recording...')

            while self._running:
                try:
                    self.main_q.get_nowait()
                except asyncio.QueueEmpty:
                    break
        
            self.vad.reset()
            chunks = []

            while self._running and not self.vad.is_speech_done():
                data = await self.main_q.get()
                chunk = np.frombuffer(data, dtype=np.int16)
                chunks.append(chunk)
                self.vad.process_chunk(chunk)
                
                if not self._running:
                    break
            
            # ---- Speech to Text ----

            audio_float32 = np.concatenate(chunks).astype(np.float32) / 32768.0
            text = await asyncio.to_thread(self.stt.transcribe, audio_float32)
            print('User:', text)

            # ---- Language Model & Text to Speech ----
            await self._respond(text)

            # Loop back to top

        self.ww_q.put_nowait(None) # Stop wake word monitor
        self.main_q.put_nowait(None) # Stop audio stream
        self.audio.cleanup()
    
    async def stop(self):
        self._running = False
        self.wake_word_monitor.triggered.set()  # unblock engine's wait
        self.ww_q.put_nowait(None) # We put None again to ensure the wake word monitor and main queue exit if it's waiting on the event
        self.main_q.put_nowait(None)