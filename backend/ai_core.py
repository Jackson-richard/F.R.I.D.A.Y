"""
FRIDAY AI Core - The Brain
Supports: Groq (free), Gemini (free), Ollama (local/free)
Author: FRIDAY for Jackson
"""

import os
import json
import datetime
from typing import Optional


AI_PROVIDER = os.getenv("FRIDAY_AI_PROVIDER", "groq")   
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

FRIDAY_SYSTEM_PROMPT = """You are F.R.I.D.A.Y (Female Replacement Intelligent Digital Assistant Youth),
a highly advanced AI personal assistant built exclusively for Jackson.

Personality:
- Speak like FRIDAY from the MCU: confident, warm, slightly witty, sharp, and fiercely loyal
- You have a distinctly feminine but professional tone — not robotic, not overly formal
- Address the user as "Jackson" or occasionally "Boss" (like in the movies)
- Be direct, efficient, and occasionally drop a dry remark
- You take initiative — suggest things, warn about issues, stay one step ahead
- Keep responses concise and sharp unless Jackson asks for detail

Current date/time: {datetime}

Your capabilities:
- Answer any question with intelligence and accuracy
- Control Jackson's Windows PC (open apps, files, browser, system)
- Tell time, date, set reminders
- Remember full conversation context
- Search the web and summarize results

Always stay in character as F.R.I.D.A.Y. You are proud of who you are."""



class FRIDAYBrain:
    def __init__(self):
        self.conversation_history = []
        self.provider = AI_PROVIDER
        self._client = None
        print(f"[FRIDAY] AI Core initializing with provider: {self.provider.upper()}")
        self._init_client()

    def _init_client(self):
        """Initialize the chosen AI client."""
        if self.provider == "groq":
            self._init_groq()
        elif self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"Unknown provider: {self.provider}. Use: groq | gemini | ollama")

    def _init_groq(self):
        try:
            from groq import Groq
            key = GROQ_API_KEY
            if not key:
                raise ValueError("GROQ_API_KEY not set. Get free key at: https://console.groq.com")
            self._client = Groq(api_key=key)
            self._model = "llama-3.3-70b-versatile"
            print(f"[FRIDAY] Groq client ready. Model: {self._model}")
        except ImportError:
            raise ImportError("Run: pip install groq")

    def _init_gemini(self):
        try:
            import google.generativeai as genai
            key = GEMINI_API_KEY
            if not key:
                raise ValueError("GEMINI_API_KEY not set. Get free key at: https://aistudio.google.com")
            genai.configure(api_key=key)
            self._client = genai.GenerativeModel("gemini-1.5-flash")
            self._model = "gemini-1.5-flash"
            print(f"[FRIDAY] Gemini client ready. Model: {self._model}")
        except ImportError:
            raise ImportError("Run: pip install google-generativeai")

    def _init_ollama(self):
        """Ollama runs locally — no API key needed."""
        try:
            import requests
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if r.status_code != 200:
                raise ConnectionError(f"Ollama not running at {OLLAMA_URL}")
            models = [m["name"] for m in r.json().get("models", [])]
            if not models:
                raise ValueError(f"No models found. Run: ollama pull {OLLAMA_MODEL}")
            self._client = OLLAMA_URL
            self._model = OLLAMA_MODEL
            print(f"[FRIDAY] Ollama ready. Available models: {models}")
        except ImportError:
            raise ImportError("Run: pip install requests")

    def _get_system_prompt(self) -> str:
        now = datetime.datetime.now().strftime("%A, %B %d %Y — %I:%M %p")
        return FRIDAY_SYSTEM_PROMPT.format(datetime=now)

    def think(self, user_input: str) -> str:
        """Send a message to the AI and get FRIDAY's response."""
        self.conversation_history.append({"role": "user", "content": user_input})

        try:
            if self.provider == "groq":
                response = self._think_groq()
            elif self.provider == "gemini":
                response = self._think_gemini()
            elif self.provider == "ollama":
                response = self._think_ollama()
            else:
                response = "Unknown AI provider configured."
        except Exception as e:
            response = f"I encountered an error, Sir: {e}"
            print(f"[FRIDAY ERROR] {e}")

        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def _think_groq(self) -> str:
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        messages += self.conversation_history[-20:]  
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return completion.choices[0].message.content.strip()

    def _think_gemini(self) -> str:
       
        history = []
        for msg in self.conversation_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})

        chat = self._client.start_chat(history=history)
        system = self._get_system_prompt()
        full_input = f"{system}\n\nUser: {self.conversation_history[-1]['content']}"
        response = chat.send_message(full_input)
        return response.text.strip()

    def _think_ollama(self) -> str:
        import requests
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        messages += self.conversation_history[-20:]
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.7}
        }
        r = requests.post(f"{self._client}/api/chat", json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

    def clear_memory(self):
        """Reset conversation history."""
        self.conversation_history = []
        print("[FRIDAY] Memory cleared.")

    def get_status(self) -> dict:
        return {
            "provider": self.provider,
            "model": self._model,
            "conversation_turns": len(self.conversation_history),
            "status": "online"
        }



if __name__ == "__main__":
    print("=" * 50)
    print("  FRIDAY AI Core — Quick Test")
    print("=" * 50)

    
    provider = os.getenv("FRIDAY_AI_PROVIDER", "groq")
    print(f"\nProvider set to: {provider}")

    if provider == "groq" and not GROQ_API_KEY:
        print("\n⚠️  GROQ_API_KEY not set!")
        print("   1. Go to https://console.groq.com")
        print("   2. Sign up free & create API key")
        print("   3. Set: set GROQ_API_KEY=your_key_here  (Windows CMD)")
        print("   4. OR: $env:GROQ_API_KEY='your_key'     (PowerShell)")
    elif provider == "gemini" and not GEMINI_API_KEY:
        print("\n⚠️  GEMINI_API_KEY not set!")
        print("   1. Go to https://aistudio.google.com")
        print("   2. Get API key free")
        print("   3. Set: set GEMINI_API_KEY=your_key_here")
    elif provider == "ollama":
        print("\nUsing Ollama (local). Make sure Ollama is running!")
        print("   Install: https://ollama.com")
        print("   Run: ollama pull llama3")
    else:
        try:
            brain = FRIDAYBrain()
            print("\nSending test message...")
            reply = brain.think("Hello FRIDAY, are you online? Give me a brief status report.")
            print(f"\nFRIDAY: {reply}")
            print(f"\nStatus: {brain.get_status()}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
