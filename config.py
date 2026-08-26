"""
Configuration module for JARVIS / Alexa Voice Assistant.
Cross-platform settings, wake words, voice preferences, routines, and AI integrations.
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = os.path.join(BASE_DIR, "jarvis_data.json")
PLUGINS_DIR = os.path.join(BASE_DIR, "skills", "plugins")

# User & Assistant identity
USER_NAME = os.environ.get("JARVIS_USER_NAME", "User")
ASSISTANT_NAME = "Jarvis"  # Can also be set to "Alexa"
WAKE_WORDS = [
    "jarvis",
    "alexa",
    "hey jarvis",
    "hey alexa",
    "computer",
    "echo",
    "assistant",
    "friday"
]

# Voice and Audio Configuration
# Genders: 'female', 'male'
VOICE_GENDER = "female"
VOICE_RATE = 175         # Normal speed of speech (WPM)
VOICE_VOLUME = 1.0       # Normal volume level (0.0 to 1.0)
ENABLE_CHIMES = True     # Audio feedback for wake word and timers

# Alexa Follow-Up Mode & Whisper Mode
ENABLE_FOLLOW_UP_MODE = True    # Keeps listening for 5 seconds after responding
FOLLOW_UP_TIMEOUT = 5           # Seconds to wait for follow-up query
ENABLE_WHISPER_MODE = True      # Speaks quietly if user whispers or at night
WHISPER_VOICE_RATE = 140
WHISPER_VOICE_VOLUME = 0.4

# Speech Recognition Settings
SPEECH_LANGUAGE = "en-US" # e.g., 'en-US', 'en-GB', 'en-IN'
ENERGY_THRESHOLD = 300    # Ambient noise sensitivity threshold
LISTEN_TIMEOUT = 5        # Seconds to wait for audio input
PHRASE_TIME_LIMIT = 8     # Max length of a spoken command in seconds

# Weather Configuration
DEFAULT_CITY = "London"
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

# News RSS Feeds
NEWS_FEEDS = {
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "tech": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "top": "https://feeds.bbci.co.uk/news/rss.xml"
}

# AI Brain Configuration (Supports Local Ollama, Google Gemini, and OpenAI)
# AI_PROVIDER: 'auto', 'gemini', 'ollama', 'openai', 'offline'
AI_PROVIDER = os.environ.get("AI_PROVIDER", "auto")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-1.5-flash"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-3.5-turbo"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

# Common applications mapping across operating systems
APP_PATHS = {
    "chrome": {
        "darwin": "Google Chrome",
        "windows": "chrome.exe",
        "linux": "google-chrome"
    },
    "firefox": {
        "darwin": "Firefox",
        "windows": "firefox.exe",
        "linux": "firefox"
    },
    "safari": {
        "darwin": "Safari",
        "windows": None,
        "linux": None
    },
    "edge": {
        "darwin": "Microsoft Edge",
        "windows": "msedge.exe",
        "linux": "microsoft-edge"
    },
    "code": {
        "darwin": "Visual Studio Code",
        "windows": "Code.exe",
        "linux": "code"
    },
    "vscode": {
        "darwin": "Visual Studio Code",
        "windows": "Code.exe",
        "linux": "code"
    },
    "spotify": {
        "darwin": "Spotify",
        "windows": "Spotify.exe",
        "linux": "spotify"
    },
    "calculator": {
        "darwin": "Calculator",
        "windows": "calc.exe",
        "linux": "gnome-calculator"
    },
    "terminal": {
        "darwin": "Terminal",
        "windows": "cmd.exe",
        "linux": "gnome-terminal"
    },
    "notes": {
        "darwin": "Notes",
        "windows": "notepad.exe",
        "linux": "gedit"
    },
    "notepad": {
        "darwin": "TextEdit",
        "windows": "notepad.exe",
        "linux": "gedit"
    },
    "finder": {
        "darwin": "Finder",
        "windows": "explorer.exe",
        "linux": "nautilus"
    },
    "explorer": {
        "darwin": "Finder",
        "windows": "explorer.exe",
        "linux": "nautilus"
    }
}
