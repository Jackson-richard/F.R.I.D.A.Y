
import os
import queue
import threading
import tempfile
import wave
import time


WAKE_WORDS = ["friday", "hey friday", "okay friday", "f.r.i.d.a.y", "hi friday"]
SILENCE_THRESHOLD = 500      
SILENCE_DURATION = 2.0       
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024


class VoiceInput:
    def __init__(self, use_whisper: bool = True):
        self.use_whisper = use_whisper
        self.is_listening = False
        self._whisper_model = None
        self._audio_queue = queue.Queue()
        print(f"[VOICE] Initializing Voice Input (whisper={use_whisper})")
        self._init_recognizer()

    def _init_recognizer(self):
        if self.use_whisper:
            try:
                from faster_whisper import WhisperModel
               
                self._whisper_model = WhisperModel(
                    "base",
                    device="cpu",
                    compute_type="int8"
                )
                print("[VOICE] Whisper model loaded (base, CPU, int8)")
            except ImportError:
                print("[VOICE] faster-whisper not found. Falling back to Google STT.")
                print("        Install: pip install faster-whisper")
                self.use_whisper = False

        if not self.use_whisper:
            try:
                import speech_recognition as sr
                self._recognizer = sr.Recognizer()
                self._recognizer.energy_threshold = 4000
                self._recognizer.dynamic_energy_threshold = True
                print("[VOICE] SpeechRecognition ready (Google free tier)")
            except ImportError:
                raise ImportError("Run: pip install SpeechRecognition pyaudio")

    def listen_once(self, timeout: int = 10, phrase_limit: int = 15) -> str:
        """
        Listen for one command and return transcribed text.
        Returns empty string if nothing heard.
        """
        print("[VOICE] Listening...")

        if self.use_whisper:
            return self._listen_whisper(timeout, phrase_limit)
        else:
            return self._listen_google(timeout, phrase_limit)

    def _listen_whisper(self, timeout: int, phrase_limit: int) -> str:
        """Record audio then transcribe with Whisper."""
        try:
            import pyaudio
            import numpy as np

            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )

            frames = []
            silent_chunks = 0
            speaking_started = False
            max_chunks = int(SAMPLE_RATE / CHUNK_SIZE * (timeout + phrase_limit))
            silence_chunks_limit = int(SAMPLE_RATE / CHUNK_SIZE * SILENCE_DURATION)

            print("[VOICE] 🎙️  Speak now...")

            for _ in range(max_chunks):
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                frames.append(data)

                
                audio_data = np.frombuffer(data, dtype=np.int16)
                amplitude = np.abs(audio_data).mean()

                if amplitude > SILENCE_THRESHOLD:
                    speaking_started = True
                    silent_chunks = 0
                elif speaking_started:
                    silent_chunks += 1
                    if silent_chunks > silence_chunks_limit:
                        break  

            stream.stop_stream()
            stream.close()
            p.terminate()

            if not speaking_started:
                print("[VOICE] No speech detected.")
                return ""

            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
                with wave.open(tmp_path, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(b''.join(frames))

            segments, _ = self._whisper_model.transcribe(
                tmp_path, beam_size=5, language="en"
            )
            text = " ".join([seg.text for seg in segments]).strip()
            os.unlink(tmp_path)

            print(f"[VOICE] Heard: '{text}'")
            return text

        except Exception as e:
            print(f"[VOICE ERROR] Whisper listen failed: {e}")
            return ""

    def _listen_google(self, timeout: int, phrase_limit: int) -> str:
        """Use Google free STT via SpeechRecognition."""
        try:
            import speech_recognition as sr
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("[VOICE] 🎙️  Speak now...")
                try:
                    audio = self._recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_limit
                    )
                    text = self._recognizer.recognize_google(audio)
                    print(f"[VOICE] Heard: '{text}'")
                    return text
                except sr.WaitTimeoutError:
                    print("[VOICE] No speech detected (timeout).")
                    return ""
                except sr.UnknownValueError:
                    print("[VOICE] Could not understand audio.")
                    return ""
        except Exception as e:
            print(f"[VOICE ERROR] Google STT failed: {e}")
            return ""

    def detect_wake_word(self, text: str) -> tuple[bool, str]:
        """
        Check if text contains a wake word.
        Returns (detected: bool, command_after_wake_word: str)
        """
        text_lower = text.lower().strip()
        for wake in WAKE_WORDS:
            if text_lower.startswith(wake):
                command = text_lower[len(wake):].strip(" ,.")
                return True, command
            elif wake in text_lower:
                idx = text_lower.index(wake)
                command = text_lower[idx + len(wake):].strip(" ,.")
                return True, command
        return False, text

    def listen_for_wake_word(self) -> str:
        """
        Continuously listen until wake word detected.
        Returns the command after the wake word.
        """
        print(f"[VOICE] Waiting for wake word: {WAKE_WORDS}")
        while True:
            text = self.listen_once(timeout=5, phrase_limit=5)
            if text:
                detected, command = self.detect_wake_word(text)
                if detected:
                    print(f"[VOICE] Wake word detected! Command: '{command}'")
                    return command
            time.sleep(0.1)


if __name__ == "__main__":
    print("=" * 50)
    print("  FRIDAY Voice Input — Test")
    print("=" * 50)
    try:
        vi = VoiceInput(use_whisper=False)  
        print("\nSay something (you have 10 seconds)...")
        result = vi.listen_once()
        if result:
            print(f"\n✅ Transcribed: '{result}'")
            wake, cmd = vi.detect_wake_word(result)
            print(f"   Wake word detected: {wake}")
            if cmd:
                print(f"   Command: '{cmd}'")
        else:
            print("❌ Nothing heard. Check your microphone!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have a microphone connected and run:")
        print("   pip install SpeechRecognition pyaudio")
