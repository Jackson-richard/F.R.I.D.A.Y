"""
FRIDAY — Female Replacement Intelligent Digital Assistant Youth
Main Entry Point — Ties everything together
Author: FRIDAY for Jackson ❤️

Usage:
    python main.py              → Text mode (safe to test first)
    python main.py --voice      → Voice mode (requires mic + speakers)
    python main.py --setup      → Guided setup wizard
"""

import os
import sys
import time
import argparse
import threading



BOOT_ART = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                   
║                                                              ║
║         Female Replacement Intelligent Digital Assistant Youth                ║
║                  Built for Jackson ⚡                        ║
╚══════════════════════════════════════════════════════════════╝
"""


def run_setup():
    print("\n" + "="*60)
    print("  FRIDAY Setup Wizard")
    print("="*60)
    print("\nChoose your AI provider (all FREE):")
    print("  1. Groq     — Fastest, requires free API key")
    print("               → https://console.groq.com")
    print("  2. Gemini   — Google AI, requires free API key")
    print("               → https://aistudio.google.com")
    print("  3. Ollama   — 100% offline, no API key")
    print("               → https://ollama.com (install first)")
    print()

    choice = input("Enter choice (1/2/3): ").strip()

    provider_map = {"1": "groq", "2": "gemini", "3": "ollama"}
    provider = provider_map.get(choice, "groq")

    env_lines = [f'FRIDAY_AI_PROVIDER={provider}\n']

    if provider == "groq":
        key = input("\nPaste your Groq API key: ").strip()
        env_lines.append(f'GROQ_API_KEY={key}\n')
    elif provider == "gemini":
        key = input("\nPaste your Gemini API key: ").strip()
        env_lines.append(f'GEMINI_API_KEY={key}\n')
    elif provider == "ollama":
        model = input("\nOllama model name (default: llama3): ").strip() or "llama3"
        env_lines.append(f'OLLAMA_MODEL={model}\n')

    
    with open(".env", "w") as f:
        f.writelines(env_lines)

    print(f"\n✅ Config saved to .env")
    print(f"   Provider: {provider}")
    print(f"\nNext steps:")
    print("   1. Install packages:  pip install -r requirements.txt")
    print("   2. Run FRIDAY:        python main.py")
    print("   3. Voice mode:        python main.py --voice")


def load_env():
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())


class FRIDAY:
    def __init__(self, voice_mode: bool = False):
        self.voice_mode = voice_mode
        self.running = False
        self._init_modules()

    def _init_modules(self):
        """Initialize all FRIDAY subsystems."""
        print("\n[BOOT] Initializing subsystems...")

        # AI Brain
        from ai_core import FRIDAYBrain
        self.brain = FRIDAYBrain()
        print("[BOOT] ✅ AI Brain online")

        
        from system_control import SystemControl
        self.system = SystemControl()
        print("[BOOT] ✅ System Control online")

        
        self.voice_in = None
        self.voice_out = None

        if self.voice_mode:
            try:
                from voice_output import VoiceOutput
                self.voice_out = VoiceOutput()
                print("[BOOT] ✅ Voice Output online")
            except Exception as e:
                print(f"[BOOT] ⚠️  Voice Output failed: {e}")

            try:
                from voice_input import VoiceInput
                self.voice_in = VoiceInput()
                print("[BOOT] ✅ Voice Input online")
            except Exception as e:
                print(f"[BOOT] ⚠️  Voice Input failed: {e}")

        print("[BOOT] All systems initialized.\n")

    def speak(self, text: str):
        """Output text — voice if available, always print."""
        print(f"\n🤖 FRIDAY: {text}\n")
        if self.voice_out:
            self.voice_out.speak(text, block=False)

    def process(self, user_input: str) -> str:
        """Process input: try system commands first, then AI."""
        if not user_input.strip():
            return ""

        
        system_result = self.system.parse_and_execute(user_input)
        if system_result:
            return system_result

        
        lower = user_input.lower().strip()
        if lower in ["exit", "quit", "goodbye", "bye", "shutdown friday"]:
            self.running = False
            return "Goodbye, Sir. FRIDAY going offline."
        if lower in ["clear", "clear memory", "forget everything"]:
            self.brain.clear_memory()
            return "Memory cleared, Sir."
        if lower in ["status", "system status"]:
            info = self.system.get_system_info()
            status = self.brain.get_status()
            return (f"AI: {status['provider'].upper()} ({status['model']}), "
                    f"Conversation turns: {status['conversation_turns']}. "
                    f"CPU: {info.get('cpu_usage', 'N/A')}, "
                    f"RAM: {info.get('ram_percent', 'N/A')} used.")

    
        return self.brain.think(user_input)

    def run_text_mode(self):
        """Run in text/chat mode."""
        self.running = True
        greeting = "Good day, Sir. FRIDAY is online and fully operational. How may I assist you?"
        self.speak(greeting)

        print("─" * 60)
        print("  Type your command or question. Type 'exit' to quit.")
        print("  Commands: 'clear' (reset memory), 'status' (system info)")
        print("─" * 60)

        while self.running:
            try:
                user_input = input("\n👤 You: ").strip()
                if not user_input:
                    continue

                response = self.process(user_input)
                if response:
                    self.speak(response)

            except KeyboardInterrupt:
                self.speak("Keyboard interrupt detected. Going offline, Sir.")
                break
            except Exception as e:
                print(f"[ERROR] {e}")

        print("\n[FRIDAY] Offline.")

    def run_voice_mode(self):
        """Run in full voice mode."""
        if not self.voice_in or not self.voice_out:
            print("[ERROR] Voice mode requires voice_input and voice_output modules.")
            print("        Run: pip install edge-tts pygame SpeechRecognition pyaudio")
            return

        self.running = True
        greeting = "Good day, Sir. FRIDAY voice mode is active. Say 'Hey FRIDAY' followed by your command."
        self.speak(greeting)

        print("─" * 60)
        print("  🎙️  FRIDAY Voice Mode Active")
        print("  Say 'Hey FRIDAY <command>' or just speak after the beep")
        print("  Press Ctrl+C to exit")
        print("─" * 60)

        while self.running:
            try:
                
                text = self.voice_in.listen_once(timeout=8, phrase_limit=15)

                if not text:
                    continue

                
                detected, command = self.voice_in.detect_wake_word(text)

                if not detected:
                    
                    command = text

                if command:
                    print(f"\n👤 You: {command}")
                    response = self.process(command)
                    if response:
                        self.speak(response)

            except KeyboardInterrupt:
                self.speak("Voice mode deactivated. Goodbye, Sir.")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(1)

        print("\n[FRIDAY] Voice mode offline.")


# ── ENTRY POINT ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    load_env()

    parser = argparse.ArgumentParser(description="FRIDAY Personal Assistant")
    parser.add_argument("--voice", action="store_true", help="Enable voice mode")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    args = parser.parse_args()

    print(BOOT_ART)

    if args.setup:
        run_setup()
        sys.exit(0)

    friday = FRIDAY(voice_mode=args.voice)

    if args.voice:
        friday.run_voice_mode()
    else:
        friday.run_text_mode()
