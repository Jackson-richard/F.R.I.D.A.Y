# F.R.I.D.A.Y – Personal AI Assistant

F.R.I.D.A.Y (Functional Responsive Intelligent Digital Assistant for You) is a desktop AI assistant inspired by the assistants seen in science-fiction.
It combines conversational AI, voice interaction, and system control to create a natural interface between humans and their computers.

The assistant can listen to voice commands, process them using an AI model, and perform tasks such as opening applications, searching information, or controlling the system.

---

# 🚀 Features

* Conversational AI powered assistant
* Voice input using speech-to-text
* Natural voice output
* Desktop graphical interface
* Wake-word activation
* System automation and application control
* Modular architecture for easy expansion

---

# 🏗️ Tech Stack

| Layer          | Technology             | Purpose                                      |
| -------------- | ---------------------- | -------------------------------------------- |
| Language       | Python 3.11+           | Core backend logic and system interaction    |
| AI Brain       | Claude API (Anthropic) | Natural language understanding and responses |
| Voice Input    | faster-whisper         | Fast offline speech-to-text processing       |
| Voice Output   | edge-tts               | Natural sounding text-to-speech              |
| Wake Word      | pvporcupine            | Detects activation phrase like "Hey Jarvis"  |
| System Control | pyautogui + subprocess | Controls applications and OS features        |
| UI             | React + Electron       | Desktop interface with futuristic UI         |

---

# 📁 Project Structure

```
F.R.I.D.A.Y/
│
├── backend/
│   ├── main.py              # Main entry point
│   ├── ai_core.py           # AI conversation engine
│   ├── voice_input.py       # Speech recognition
│   ├── voice_output.py      # Text to speech system
│   └── system_control.py    # OS automation and commands
│
├── frontend/
│   ├── src/                 # React components
│   └── public/              # Static assets
│
├── config.py                # Configuration settings
└── requirements.txt         # Python dependencies
```

---

# ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/friday-ai.git
cd friday-ai
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
```

---

# ▶️ Running the Assistant

### Start Backend

```bash
python backend/main.py
```

### Start Frontend

```bash
cd frontend
npm start
```

---

# 🧠 Architecture Overview

F.R.I.D.A.Y is designed using a modular architecture where each component handles a specific responsibility.

**Input Layer**

* Wake word detection
* Voice capture

**Processing Layer**

* Speech to text conversion
* AI language processing via Claude API

**Action Layer**

* System command execution
* Application control
* Response generation

**Output Layer**

* Text-to-speech voice response
* Graphical UI feedback

---

# 🚀 Development Roadmap

## Phase 1 — AI Conversation Core

Build the central intelligence of the assistant.

* Claude API integration
* Prompt management
* Memory and context system

## Phase 2 — User Interface

Create a desktop interface using React and Electron.

* Futuristic assistant dashboard
* Status indicators
* Voice activity visualization

## Phase 3 — Voice Interaction

Enable natural communication.

* Speech recognition with faster-whisper
* Text-to-speech responses
* Wake word detection

## Phase 4 — System Automation

Allow the assistant to control the computer.

* Launch applications
* File management
* Web automation
* OS command execution

---

# 🔒 Security Considerations

Since the assistant can interact with the operating system, permissions and safeguards should be implemented to prevent unintended actions.

Future versions may include:

* Command confirmation
* User authentication
* Restricted command permissions

---

# 🌌 Future Improvements

* Memory system for personalized interactions
* Plugin architecture
* Integration with smart devices
* Local LLM support
* Advanced UI animations

---

# 📜 License

This project is open-source and available under the MIT License.

---

# 👨‍💻 Author

Developed as an experimental AI assistant project exploring voice interfaces, automation, and conversational AI systems.
