"""
FRIDAY Flask API Server — with fast streaming voice
"""

import os
import sys
import threading
import asyncio
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

def load_env():
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())

load_env()

app = Flask(__name__)
CORS(app)


try:
    from core.brain_v2 import FRIDAYBrainV2
    from system_control import SystemControl
    brain = FRIDAYBrainV2()
    system = SystemControl()
    print("[SERVER] ✅ FRIDAY Neural Core (V2) and system control initialized")
except Exception as e:
    print(f"[SERVER] ❌ Failed to initialize: {e}")
    sys.exit(1)

voice_enabled = True
try:
    import edge_tts
    import pygame
    pygame.mixer.pre_init(44100, -16, 2, 512)  
    pygame.mixer.init()
    print("[SERVER] ✅ Voice ready — streaming mode (low latency)")
except ImportError as e:
    voice_enabled = False
    print(f"[SERVER] ⚠️  Voice unavailable: {e}")


def clean_text(text: str) -> str:
    """Strip markdown so FRIDAY doesn't say 'asterisk asterisk'."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*',     r'\1', text)
    text = re.sub(r'`(.+?)`',       r'\1', text)
    text = re.sub(r'#{1,6}\s',      '',    text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    text = re.sub(r'\n+',           '. ',  text)
    
    text = re.sub(r'\*[^*]+\*',     '',    text)
    return text.strip()


def speak_async(text: str):
    """
    Stream audio bytes directly into pygame — NO temp file, NO save delay.
    Starts playing within ~300ms.
    """
    if not voice_enabled or not text:
        return

    def _run():
        try:
            import io
            import edge_tts
            import pygame

            clean = clean_text(text)
            if not clean:
                return

           
            async def _stream():
                communicate = edge_tts.Communicate(
                    clean,
                    voice="en-IE-EmilyNeural",
                    rate="+8%",
                    pitch="-5Hz"
                )
                audio_bytes = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_bytes += chunk["data"]
                return audio_bytes

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_bytes = loop.run_until_complete(_stream())
            loop.close()

            if not audio_bytes:
                print("[SPEECH] No audio bytes received")
                return

            
            audio_buffer = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(audio_buffer, "mp3")
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(15)

            pygame.mixer.music.stop()

        except Exception as e:
            print(f"[SPEECH ERROR] {e}")

    threading.Thread(target=_run, daemon=True).start()



@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "friday": "operational",
        "voice": "streaming" if voice_enabled else "unavailable"
    })


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_msg = data["message"].strip()
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    # No more hardcoded string matching. Everything goes through the V2 Brain (Tool Calling).
    try:
        response = brain.think(user_msg)
        speak_async(response)
        return jsonify({"response": response, "source": "ai"})
    except Exception as e:
        err_msg = f"I ran into an error, Boss: {e}"
        speak_async(err_msg)
        return jsonify({"response": err_msg, "source": "error"}), 500


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "ai": brain.get_status(),
        "system": system.get_system_info()
    })


@app.route("/clear", methods=["POST"])
def clear_memory():
    brain.clear_memory()
    msg = "Memory cleared, Jackson."
    speak_async(msg)
    return jsonify({"status": msg})


@app.route("/speak", methods=["POST"])
def speak_endpoint():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text"}), 400
    speak_async(text)
    return jsonify({"status": "Speaking"})



if __name__ == "__main__":
    print("\n" + "="*50)
    print("  F.R.I.D.A.Y API Server — Streaming Voice")
    print("="*50)
    print(f"\n  Backend:  http://localhost:5000")
    print(f"  Voice:    {'✅ streaming (fast)' if voice_enabled else '⚠️  unavailable'}")
    print(f"  Frontend: Open frontend/index.html in Chrome")
    print("\n  Press Ctrl+C to stop\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
