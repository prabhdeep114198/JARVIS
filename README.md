# 🤖 JARVIS / Alexa Cross-Platform Voice Assistant & Smart Display

An intelligent, multi-platform AI voice assistant inspired by **Amazon Alexa** and **JARVIS**. Runs seamlessly across **macOS**, **Windows**, and **Linux** with native OS integration, Alexa-style routines, multi-turn follow-up mode, modular plugins, ambient sleep sounds, multi-provider AI brain, and an **Echo Show Smart Display GUI**.

---

## ✨ Features & Architecture

- 🎙️ **Alexa-like Wake Word Detection**: Passive standby listening for `"Jarvis"`, `"Alexa"`, `"Computer"`, or `"Echo"` with chime audio cues.
- 🔄 **Follow-Up Mode**: After answering, keeps listening for 5 seconds for follow-up questions without needing the wake word again.
- 🌅 **Alexa Routines & Automation**:
  - *"Start my day"* / *"Good morning"*: Greets, reads live weather, agenda/reminders, and news flash brief.
  - *"Focus mode"* / *"Coding mode"*: Opens VS Code, starts a 25-minute Pomodoro timer, and plays Lo-Fi focus beats.
  - *"Bedtime routine"*: Adjusts night volume, checks tomorrow's agenda, and bids good night.
- 🧠 **Multi-Provider AI Brain with Context Memory**:
  - **Local Ollama** (100% offline, free & private with Llama 3 / Mistral / DeepSeek).
  - **Google Gemini API** (High-speed conversational answers via `GEMINI_API_KEY`).
  - **OpenAI API** (`OPENAI_API_KEY`).
- 🧩 **Modular Plugin Architecture (`skills/plugins/`)**:
  - 📈 **Crypto & Stocks**: Live Bitcoin, Ethereum, Solana, and stock quotes.
  - 🌐 **Instant Multi-Language Translator**: Spanish, French, German, Japanese, Hindi, Chinese, etc.
  - 🎯 **Interactive Trivia & Quiz Game**: General knowledge questions via Open Trivia DB.
- 🌧️ **Ambient Sleep Sounds & Radio**:
  - *"Play rain sounds"*, *"Play ocean waves"*, *"Play fireplace sounds"*, *"Play white noise"*, *"Play Lo-Fi radio"*.
- 🖥️ **Echo Show Smart Display Desktop UI (`--gui`)**:
  - Dark-themed desktop dashboard with a pulsating animated glowing Alexa orb, digital clock, live weather, timer countdowns, and speech subtitles.
- ⏰ **Background Timers & Alarms**: Multi-timer management with acoustic alarm alerts.
- 🌤️ **Global Weather**: Powered by Open-Meteo (no API keys required!).
- 💻 **Cross-Platform OS Controls**: App launcher, battery monitoring, volume adjustments, screenshot capture, and screen locking.

---

## 🚀 Quick Start

### 1. Installation

#### **macOS**
```bash
brew install portaudio
pip install -r requirements.txt
```

#### **Windows**
```bash
pip install -r requirements.txt
```

#### **Linux (Ubuntu / Debian)**
```bash
sudo apt update && sudo apt install -y python3-pyaudio espeak portaudio19-dev
pip install -r requirements.txt
```

---

## 🎯 Running JARVIS

### 1. Echo Show Smart Display GUI Mode (Voice + Visual Display)
```bash
python3 jarvis.py --gui
```

### 2. Standard Voice Mode (Wake Word Standby)
```bash
python3 jarvis.py
```

### 3. Interactive Text Mode (No Microphone Needed)
```bash
python3 jarvis.py --text
```

### 4. Continuous Voice Mode (No Wake Word Required)
```bash
python3 jarvis.py --no-wake
```

---

## 🗣️ Voice Commands Cheatsheet

| Category | Example Voice Commands |
| :--- | :--- |
| **Routines** | *"Start my day"*, *"Good morning"*, *"Focus mode"*, *"Bedtime routine"* |
| **Crypto & Stocks** | *"What is Bitcoin trading at?"*, *"Check Ethereum price"*, *"What is Solana at?"* |
| **Translation** | *"Translate good morning in Spanish"*, *"How do you say thank you in French?"* |
| **Trivia** | *"Give me a trivia question"*, *"Start trivia"*, *"Play quiz"* |
| **Ambient Sounds** | *"Play rain sounds"*, *"Play ocean waves"*, *"Play white noise"*, *"Play fireplace sounds"* |
| **Weather** | *"What's the weather in Tokyo?"*, *"How's the forecast for London?"* |
| **Timers** | *"Set a timer for 10 minutes"*, *"Set a 5-minute timer for tea"*, *"Timer status"*, *"Cancel timer"* |
| **Media** | *"Play Queen on YouTube"*, *"Play Blinding Lights on Spotify"*, *"Open YouTube"* |
| **News** | *"What's the news?"*, *"Read the latest tech headlines"* |
| **Math & Units** | *"What is 15 percent of 850?"*, *"Convert 10 miles to kilometers"*, *"Square root of 144"* |
| **Reminders** | *"Remind me to call John at 5 PM"*, *"What are my reminders?"*, *"Clear reminders"* |
| **System** | *"Open Visual Studio Code"*, *"Take a screenshot"*, *"What is my battery level?"*, *"Volume up"*, *"Mute"* |
| **Knowledge & AI** | *"Who was Marie Curie?"*, *"Explain quantum computing"*, *"Search Google for Python"* |
| **Fun & Games** | *"Tell me a joke"*, *"Flip a coin"*, *"Roll a die"*, *"Simon says wake up"* |

---

## ⚙️ Configuration (`config.py`)

- `ASSISTANT_NAME`: Name of the assistant (`"Jarvis"` or `"Alexa"`).
- `USER_NAME`: Your name for personalized greetings.
- `ENABLE_FOLLOW_UP_MODE`: `True` / `False` (Alexa-style follow-up listening).
- `AI_PROVIDER`: Choose `'auto'`, `'gemini'`, `'ollama'`, `'openai'`, or `'offline'`.
- `GEMINI_API_KEY` / `OPENAI_API_KEY`: Optional keys for cloud LLM intelligence.
- `OLLAMA_URL` / `OLLAMA_MODEL`: For local offline LLM intelligence (default: `llama3`).
