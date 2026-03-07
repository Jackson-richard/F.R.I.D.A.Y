"""
FRIDAY Voice Output — Text-to-Speech
Uses edge-tts (Microsoft Neural voices — FREE, no API key)
Fallback: pyttsx3 (fully offline)
"""

import os
import asyncio
import tempfile
import threading



VOICE_OPTIONS = {
    "friday":   "en-GB-RyanNeural",     
    "friday":   "en-IE-EmilyNeural",      
    "us_male":  "en-US-GuyNeural",         
    "us_female":"en-US-JennyNeural",       
}

DEFAULT_VOICE = VOICE_OPTIONS["friday"]  
SPEECH_RATE  = "+5%"     
SPEECH_PITCH = "-5Hz"    


class VoiceOutput:
    def __init__(self, use_edge_tts: bool = True, voice: str = DEFAULT_VOICE):
        self.use_edge_tts = use_edge_tts
        self.voice = voice
        self._lock = threading.Lock()
        self._speaking = False
        print(f"[SPEECH] Initializing Voice Output (edge_tts={use_edge_tts})")
        self._init_engine()

    def _init_engine(self):
        if self.use_edge_tts:
            try:
                import edge_tts
                print(f"[SPEECH] edge-tts ready. Voice: {self.voice}")
            except ImportError:
                print("[SPEECH] edge-tts not found. Falling back to pyttsx3.")
                print("         Install: pip install edge-tts")
                self.use_edge_tts = False

        if not self.use_edge_tts:
            try:
                import pyttsx3
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", 175)
                self._engine.setProperty("volume", 1.0)
                # Try to set a male voice
                voices = self._engine.getProperty("voices")
                for v in voices:
                    if "david" in v.name.lower() or "male" in v.name.lower():
                        self._engine.setProperty("voice", v.id)
                        break
                print(f"[SPEECH] pyttsx3 ready (offline fallback)")
            except ImportError:
                raise ImportError("Run: pip install pyttsx3")

    def speak(self, text: str, block: bool = True):
        """
        Convert text to speech and play it.
        block=True  → wait until done speaking
        block=False → speak in background thread
        """
        if not text or not text.strip():
            return

        
        clean = self._clean_text(text)

        if block:
            self._speak_internal(clean)
        else:
            t = threading.Thread(target=self._speak_internal, args=(clean,), daemon=True)
            t.start()

    def _speak_internal(self, text: str):
        with self._lock:
            self._speaking = True
            try:
                if self.use_edge_tts:
                    asyncio.run(self._speak_edge(text))
                else:
                    self._speak_pyttsx3(text)
            except Exception as e:
                print(f"[SPEECH ERROR] {e}")
                # Try fallback
                try:
                    self._speak_pyttsx3(text)
                except:
                    print(f"[SPEECH] Could not speak: '{text[:50]}...'")
            finally:
                self._speaking = False

    async def _speak_edge(self, text: str):
        """Use Microsoft edge-tts (free, high quality neural voice)."""
        import edge_tts
        import pygame

        communicate = edge_tts.Communicate(
            text,
            voice=self.voice,
            rate=SPEECH_RATE,
            pitch=SPEECH_PITCH
        )

        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        await communicate.save(tmp_path)
        self._play_audio(tmp_path)
        os.unlink(tmp_path)

    def _play_audio(self, filepath: str):
        """Play audio file using pygame (cross-platform)."""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except ImportError:
            
            import subprocess
            subprocess.run(
                ["powershell", "-c", f'(New-Object Media.SoundPlayer "{filepath}").PlaySync()'],
                capture_output=True
            )

    def _speak_pyttsx3(self, text: str):
        """Fully offline fallback TTS."""
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()

    def _clean_text(self, text: str) -> str:
        """Remove markdown formatting from text before speaking."""
        import re
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)   
        text = re.sub(r'\*(.+?)\*', r'\1', text)         
        text = re.sub(r'`(.+?)`', r'\1', text)           
        text = re.sub(r'#{1,6}\s', '', text)              
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  
        text = re.sub(r'\n+', '. ', text)                 
        return text.strip()

    @property
    def is_speaking(self) -> bool:
        return self._speaking

    def set_voice(self, voice_key: str):
        """Change voice. Options: friday, friday, us_male, us_female"""
        if voice_key in VOICE_OPTIONS:
            self.voice = VOICE_OPTIONS[voice_key]
            print(f"[SPEECH] Voice changed to: {self.voice}")
        else:
            print(f"[SPEECH] Unknown voice '{voice_key}'. Options: {list(VOICE_OPTIONS.keys())}")


if __name__ == "__main__":
    print("=" * 50)
    print("  FRIDAY Voice Output — Test")
    print("=" * 50)

    try:
        tts = VoiceOutput(use_edge_tts=True)
        test_lines = [
            "Good day, Sir. FRIDAY online and fully operational.",
            "All systems nominal. How may I assist you today, Jackson?"
        ]
        for line in test_lines:
            print(f"\n Speaking: '{line}'")
            tts.speak(line)
        print("\n✅ Voice test complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nInstall required packages:")
        print("   pip install edge-tts pygame")
        print("   OR: pip install pyttsx3")
