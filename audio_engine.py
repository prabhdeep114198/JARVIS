"""
Cross-platform Audio Engine for JARVIS / Alexa.
Handles Speech Recognition (STT), Text-to-Speech (TTS), Whisper Mode,
and Audio Chimes across macOS, Windows, and Linux.
"""

import math
import os
import platform
import struct
import subprocess
import sys
import tempfile
import threading
import time
import wave

import config

CURRENT_OS = platform.system().lower()  # 'darwin', 'windows', 'linux'

# Global UI speech callback (e.g. for GUI subtitles / visualizer)
SPEECH_OBSERVERS = []


def register_speech_observer(cb):
    """Registers a callback for speech events (text, state)."""
    if cb not in SPEECH_OBSERVERS:
        SPEECH_OBSERVERS.append(cb)


def notify_speech_observers(text: str, state: str = "speaking"):
    for cb in SPEECH_OBSERVERS:
        try:
            cb(text, state)
        except Exception:
            pass


# Try importing speech_recognition
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

# Try importing pyttsx3
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False


class TTSEngine:
    """Cross-platform Text-To-Speech engine with Whisper Mode support."""

    def __init__(self):
        self.engine = None
        self.use_native_fallback = False
        self._init_pyttsx3()

    def _init_pyttsx3(self):
        if not HAS_PYTTSX3:
            self.use_native_fallback = True
            return

        try:
            if CURRENT_OS == "darwin":
                try:
                    self.engine = pyttsx3.init('nsss')
                except Exception:
                    self.engine = pyttsx3.init()
            elif CURRENT_OS == "windows":
                try:
                    self.engine = pyttsx3.init('sapi5')
                except Exception:
                    self.engine = pyttsx3.init()
            else:
                try:
                    self.engine = pyttsx3.init('espeak')
                except Exception:
                    self.engine = pyttsx3.init()

            self.engine.setProperty('rate', config.VOICE_RATE)
            self.engine.setProperty('volume', config.VOICE_VOLUME)

            voices = self.engine.getProperty('voices')
            if voices:
                selected_voice = None
                target_gender = config.VOICE_GENDER.lower()

                for v in voices:
                    v_name = (v.name or "").lower()
                    v_id = (v.id or "").lower()
                    v_gender = getattr(v, 'gender', '').lower() if hasattr(v, 'gender') else ''

                    if target_gender in v_gender or target_gender in v_name or target_gender in v_id:
                        selected_voice = v.id
                        break
                    if target_gender == "female" and any(name in v_name for name in ["samantha", "zira", "victoria", "karen"]):
                        selected_voice = v.id
                        break
                    elif target_gender == "male" and any(name in v_name for name in ["david", "alex", "daniel"]):
                        selected_voice = v.id
                        break

                if not selected_voice:
                    if len(voices) > 1 and target_gender == "female":
                        selected_voice = voices[1].id
                    else:
                        selected_voice = voices[0].id

                self.engine.setProperty('voice', selected_voice)

        except Exception:
            self.use_native_fallback = True
            self.engine = None

    def speak(self, text: str, whisper: bool = False):
        """Speak the given text and display it in console / GUI."""
        if not text:
            return
        
        notify_speech_observers(text, state="speaking")

        prefix = "💬 \033[1;35m[Whisper] " if whisper else "💬 \033[1;36m"
        print(f"\n{prefix}{config.ASSISTANT_NAME}:\033[0m {text}")

        rate = config.WHISPER_VOICE_RATE if whisper else config.VOICE_RATE
        vol = config.WHISPER_VOICE_VOLUME if whisper else config.VOICE_VOLUME

        if self.engine and not self.use_native_fallback:
            try:
                self.engine.setProperty('rate', rate)
                self.engine.setProperty('volume', vol)
                self.engine.say(text)
                self.engine.runAndWait()
                notify_speech_observers(text, state="idle")
                return
            except Exception:
                pass

        self._speak_native(text, whisper=whisper)
        notify_speech_observers(text, state="idle")

    def _speak_native(self, text: str, whisper: bool = False):
        """Fallback TTS using platform-specific commands."""
        escaped_text = text.replace('"', '\\"').replace("'", "\\'")
        rate = config.WHISPER_VOICE_RATE if whisper else config.VOICE_RATE

        try:
            if CURRENT_OS == "darwin":
                # macOS native 'say'
                voice_arg = ["-v", "Whisper"] if whisper else (["-v", "Samantha"] if config.VOICE_GENDER == "female" else ["-v", "Alex"])
                rate_arg = ["-r", str(rate)]
                subprocess.run(["say"] + voice_arg + rate_arg + [text], check=False)

            elif CURRENT_OS == "windows":
                ps_cmd = (
                    f"Add-Type -AssemblyName System.speech; "
                    f"$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    f"$speak.Rate = 1; "
                    f"$speak.Speak('{escaped_text}');"
                )
                subprocess.run(["powershell", "-Command", ps_cmd], check=False, creationflags=0x08000000)

            elif CURRENT_OS == "linux":
                try:
                    subprocess.run(["spd-say", "-r", "10", text], check=False)
                except FileNotFoundError:
                    subprocess.run(["espeak", "-s", str(rate), text], check=False)
        except Exception:
            pass


class ChimePlayer:
    """Generates and plays Alexa-like audio tones cross-platform."""

    @staticmethod
    def play_tone(freq=880, duration_ms=120, volume=0.3):
        if not config.ENABLE_CHIMES:
            return

        def _play():
            try:
                sample_rate = 44100
                num_samples = int(sample_rate * (duration_ms / 1000.0))
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    tmp_wav = f.name

                with wave.open(tmp_wav, 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    
                    frames = bytearray()
                    for i in range(num_samples):
                        fade = 1.0
                        if i < 400:
                            fade = i / 400.0
                        elif i > num_samples - 400:
                            fade = (num_samples - i) / 400.0
                        
                        sample_val = int(volume * fade * 32767.0 * math.sin(2.0 * math.pi * freq * (i / sample_rate)))
                        frames.extend(struct.pack('<h', sample_val))
                    
                    wav_file.writeframes(frames)

                if CURRENT_OS == "darwin":
                    subprocess.run(["afplay", tmp_wav], check=False)
                elif CURRENT_OS == "windows":
                    import winsound
                    winsound.PlaySound(tmp_wav, winsound.SND_FILENAME)
                elif CURRENT_OS == "linux":
                    subprocess.run(["aplay", "-q", tmp_wav], check=False)

                if os.path.exists(tmp_wav):
                    os.remove(tmp_wav)
            except Exception:
                sys.stdout.write('\a')
                sys.stdout.flush()

        threading.Thread(target=_play, daemon=True).start()

    @classmethod
    def wake_chime(cls):
        """Alexa wake word confirmation tone."""
        def _chime():
            cls.play_tone(freq=587, duration_ms=90, volume=0.25)
            time.sleep(0.09)
            cls.play_tone(freq=880, duration_ms=130, volume=0.25)
        threading.Thread(target=_chime, daemon=True).start()

    @classmethod
    def follow_up_chime(cls):
        """Alexa gentle follow-up mode listening tone."""
        cls.play_tone(freq=740, duration_ms=80, volume=0.15)

    @classmethod
    def alarm_chime(cls):
        """Timer expiration alarm sound."""
        def _alarm():
            for _ in range(3):
                cls.play_tone(freq=784, duration_ms=150, volume=0.4)
                time.sleep(0.18)
                cls.play_tone(freq=988, duration_ms=250, volume=0.4)
                time.sleep(0.3)
        threading.Thread(target=_alarm, daemon=True).start()


class STTEngine:
    """Cross-platform Speech Recognition engine."""

    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.mic_available = False
        self._init_recognizer()

    def _init_recognizer(self):
        if not HAS_SR:
            return

        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = config.ENERGY_THRESHOLD
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 1.2
            self.recognizer.non_speaking_duration = 0.6
            self.microphone = sr.Microphone()
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.mic_available = True
        except Exception:
            self.mic_available = False

    def listen(self, timeout=config.LISTEN_TIMEOUT, phrase_time_limit=config.PHRASE_TIME_LIMIT) -> str:
        if not self.mic_available or not self.recognizer or not self.microphone:
            return ""

        try:
            with self.microphone as source:
                notify_speech_observers("", state="listening")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                notify_speech_observers("", state="processing")
                query = self.recognizer.recognize_google(
                    audio,
                    language=config.SPEECH_LANGUAGE
                )
                return query.strip().lower()
        except sr.WaitTimeoutError:
            notify_speech_observers("", state="idle")
            return ""
        except sr.UnknownValueError:
            notify_speech_observers("", state="idle")
            return ""
        except sr.RequestError:
            notify_speech_observers("", state="idle")
            print("\033[33m[STT Warning: Could not reach Google Speech API. Check internet connection.]\033[0m")
            return ""
        except Exception:
            notify_speech_observers("", state="idle")
            return ""


# Global singleton instances
tts = TTSEngine()
stt = STTEngine()
chimes = ChimePlayer()


def speak(text: str, whisper: bool = False):
    """Global helper for text-to-speech."""
    tts.speak(text, whisper=whisper)
