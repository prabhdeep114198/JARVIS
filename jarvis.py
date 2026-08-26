"""
JARVIS / Alexa AI Voice Assistant.
Cross-platform intelligent assistant with Alexa Routines, Multi-Turn Follow-Up Mode,
AI Brain (Ollama/Gemini/OpenAI), Plugins, Ambient Sounds, and Smart Display GUI.
"""

import os
import warnings
os.environ["TK_SILENCE_DEPRECATION"] = "1"
warnings.filterwarnings("ignore")

import argparse
import datetime
import platform
import random
import re
import sys
import threading
import time

import config
from audio_engine import chimes, speak, stt, tts
from skills import (
    ai_brain,
    ambient_sounds,
    calculations,
    fun_easter_eggs,
    knowledge,
    media,
    news,
    notes_reminders,
    plugin_manager,
    routines,
    system_control,
    timer_alarm,
    weather
)

CURRENT_OS = platform.system().lower()

BANNER = r"""
\033[1;36m
   ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗   █████╗ ██╗     ███████╗██╗  ██╗ █████╗ 
   ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝  ██╔══██╗██║     ██╔════╝██║  ██║██╔══██╗
   ██║███████║██████╔╝██║   ██║██║███████╗  ███████║██║     █████╗  ███████║███████║
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║  ██╔══██║██║     ██╔══╝  ██╔══██║██╔══██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║  ██║  ██║███████╗███████╗██║  ██║██║  ██║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
\033[0m
  \033[1;32m● Status: Online\033[0m  |  \033[1;34mOS: {os_name}\033[0m  |  \033[1;35mWake Words: {wake_words}\033[0m
  \033[90m--------------------------------------------------------------------------------\033[0m
"""


def display_welcome_banner():
    """Prints the startup dashboard banner with system information."""
    os_name = "macOS" if CURRENT_OS == "darwin" else ("Windows" if CURRENT_OS == "windows" else "Linux")
    wake_str = ", ".join([f"'{w}'" for w in config.WAKE_WORDS[:3]])
    print(BANNER.format(os_name=os_name, wake_words=wake_str))
    print("\033[1;33m💡 Alexa Features & Routines:\033[0m")
    print("  • \033[36m'Start my day'\033[0m                 • \033[36m'Focus mode / Coding mode'\033[0m")
    print("  • \033[36m'Play rain sounds'\033[0m              • \033[36m'What is Bitcoin trading at?'\033[0m")
    print("  • \033[36m'Translate hello to Japanese'\033[0m   • \033[36m'Start a trivia quiz'\033[0m")
    print("  • \033[36m'Set a timer for 10 minutes'\033[0m    • \033[36m'What is 15 percent of 850?'\033[0m")
    print("  • \033[36m'What's the weather in Tokyo?'\033[0m   • \033[36m'Remind me to buy groceries'\033[0m")
    print("\033[90m--------------------------------------------------------------------------------\033[0m\n")


def on_timer_completed(label: str, duration_sec: int):
    """Callback fired when a countdown timer finishes."""
    print(f"\n\033[1;31m⏰ [ALARM] {label.upper()} IS DONE!\033[0m")
    chimes.alarm_chime()
    speak(f"Your {label} is done!")


def wish_me():
    """Speaks greeting based on local time of day."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 17:
        greeting = "Good afternoon"
    elif 17 <= hour < 22:
        greeting = "Good evening"
    else:
        greeting = "Hello"

    speak(f"{greeting}, {config.USER_NAME}! I am {config.ASSISTANT_NAME}. How can I help you today?")


def extract_wake_word_query(raw_text: str):
    """
    Checks if speech starts with or contains any configured wake words.
    Returns (has_wake_word: bool, remaining_command: str)
    """
    if not raw_text:
        return False, ""

    text = raw_text.strip().lower()

    for wake in config.WAKE_WORDS:
        if text == wake:
            return True, ""
        if text.startswith(wake + " ") or text.startswith(wake + ","):
            clean_cmd = text[len(wake):].lstrip(" ,:.-")
            return True, clean_cmd
        if wake in text:
            clean_cmd = text.replace(wake, "").strip(" ,:.-")
            return True, clean_cmd

    return False, text


def execute_intent(query: str) -> bool:
    """
    Parses natural language query and routes it to the corresponding skill/routine/plugin.
    Returns False if user requested exit/stop, True otherwise.
    """
    clean = query.strip().lower()
    if not clean:
        return True

    # 1. Exit / Shutdown Commands
    if any(clean == exit_word or clean.startswith(exit_word + " ") for exit_word in ["exit", "quit", "stop", "goodbye", "bye", "terminate", "turn off", "cancel"]):
        farewells = [
            f"Goodbye, {config.USER_NAME}! Have a wonderful day.",
            "Shutting down. Let me know when you need me again.",
            "See you later! Take care."
        ]
        speak(random.choice(farewells))
        return False

    # 2. Alexa Routines ("Start My Day", "Good Morning", "Focus Mode", "Bedtime")
    if routines.check_and_execute_routine(clean, on_timer_complete=on_timer_completed):
        return True

    # 3. Ambient Sleep Sounds & Radio
    ambient_reply = ambient_sounds.check_ambient_sound_query(clean)
    if ambient_reply:
        speak(ambient_reply)
        return True

    # 4. Modular Plugins (Crypto/Stocks, Translator, Trivia)
    plugin_reply = plugin_manager.dispatch_plugin(clean)
    if plugin_reply:
        speak(plugin_reply)
        return True

    # 5. Date & Time
    if any(p in clean for p in ["what time is it", "what's the time", "current time", "tell me the time"]):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}.")
        return True

    if any(p in clean for p in ["what is today's date", "what's the date", "today's date", "what day is today", "what is the date"]):
        today_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {today_date}.")
        return True

    # 6. Weather
    if "weather" in clean or "temperature" in clean or "forecast" in clean:
        city = None
        city_match = re.search(r"(?:in|for|at)\s+([a-zA-Z\s]+)", clean)
        if city_match:
            city = city_match.group(1).strip()
        else:
            pre_match = re.search(r"([a-zA-Z\s]+)\s+(?:weather|temperature|forecast)", clean)
            if pre_match:
                candidate = pre_match.group(1).strip()
                if candidate not in ["what's the", "what is the", "tell me the", "how is the", "the"]:
                    city = candidate
        
        report = weather.get_weather(city)
        speak(report)
        return True

    # 7. Timers & Alarms
    if "timer" in clean or "alarm" in clean:
        if any(p in clean for p in ["cancel", "stop", "delete", "clear", "remove"]):
            speak(timer_alarm.cancel_timer())
        elif any(p in clean for p in ["status", "how much time", "remaining", "how long", "check"]):
            speak(timer_alarm.get_timers_status())
        else:
            speak(timer_alarm.set_timer(clean, on_complete_cb=on_timer_completed))
        return True

    # 8. Media & Music
    if (
        clean == "play"
        or clean.startswith("play ")
        or "play " in clean
        or "song" in clean
        or clean.startswith("listen to ")
        or clean.startswith("put on ")
        or clean.startswith("stream ")
    ):
        song_query = clean
        for prefix in [
            "can you please play ",
            "can you play ",
            "please play ",
            "play ",
            "listen to ",
            "put on ",
            "stream ",
            "song "
        ]:
            song_query = song_query.replace(prefix, "")
        song_query = song_query.strip()
        if not song_query or song_query == "play":
            speak("What would you like me to play?")
            return True
        speak(media.play_music(song_query))
        return True

    if clean.startswith("open youtube") or clean.startswith("open google") or clean.startswith("open spotify") or clean.startswith("open netflix"):
        site = clean.replace("open", "").strip()
        speak(media.open_website(site))
        return True

    # 9. News Flash Briefing
    if any(p in clean for p in ["news", "headlines", "flash briefing", "briefing"]):
        category = "top"
        if "tech" in clean or "technology" in clean:
            category = "tech"
        elif "world" in clean or "global" in clean:
            category = "world"
        elif "business" in clean or "market" in clean:
            category = "business"
        speak(news.get_news_headlines(category=category))
        return True

    # 10. Reminders & Notes
    if "remind" in clean or "reminder" in clean:
        if any(p in clean for p in ["read", "what are", "list", "show", "tell me", "check"]):
            speak(notes_reminders.get_reminders())
        elif any(p in clean for p in ["clear", "delete all", "remove all"]):
            speak(notes_reminders.clear_reminders())
        else:
            rem_text = re.sub(r"^(?:set\s+a\s+reminder\s+to|remind\s+me\s+to|add\s+a\s+reminder\s+to|set\s+a\s+reminder|remind\s+me|add\s+reminder)\s*", "", clean).strip()
            speak(notes_reminders.add_reminder(rem_text or clean))
        return True

    if "note" in clean or "notes" in clean:
        if any(p in clean for p in ["read", "what are", "list", "show", "tell me"]):
            speak(notes_reminders.get_notes())
        elif any(p in clean for p in ["clear", "delete all", "remove all"]):
            speak(notes_reminders.clear_notes())
        else:
            note_text = re.sub(r"^(?:take\s+a\s+note|add\s+a\s+note|make\s+a\s+note|new\s+note|note\s+that)\s*", "", clean).strip()
            speak(notes_reminders.add_note(note_text or clean))
        return True

    # 11. System Controls (Volume, Battery, Screenshot, App launcher, Lock)
    if "battery" in clean or ("power" in clean and "status" in clean):
        speak(system_control.get_battery_status())
        return True

    if "volume" in clean or "mute" in clean or "unmute" in clean:
        if "mute" in clean and "unmute" not in clean:
            speak(system_control.control_volume("mute"))
        elif "unmute" in clean:
            speak(system_control.control_volume("unmute"))
        elif "up" in clean or "raise" in clean or "increase" in clean or "higher" in clean:
            speak(system_control.control_volume("up"))
        elif "down" in clean or "lower" in clean or "decrease" in clean or "softer" in clean:
            speak(system_control.control_volume("down"))
        elif "to" in clean or "%" in clean:
            lvl_match = re.search(r"(\d+)", clean)
            lvl = int(lvl_match.group(1)) if lvl_match else None
            speak(system_control.control_volume("set", level=lvl))
        else:
            speak(system_control.control_volume("up"))
        return True

    if "screenshot" in clean or "screen shot" in clean or "capture screen" in clean:
        speak(system_control.take_screenshot())
        return True

    if "lock screen" in clean or "lock computer" in clean or "lock pc" in clean or "lock workstation" in clean:
        speak(system_control.lock_workstation())
        return True

    if clean.startswith("open ") or clean.startswith("launch ") or clean.startswith("start "):
        app_name = clean.replace("open ", "").replace("launch ", "").replace("start ", "").strip()
        if any(ext in app_name for ext in [".com", ".org", ".net", ".io", ".dev", ".edu"]) or app_name in media.POPULAR_SITES:
            speak(media.open_website(app_name))
        else:
            speak(system_control.open_application(app_name))
        return True

    # 12. Math & Unit Conversions
    if any(p in clean for p in ["calculate", "plus", "minus", "times", "multiplied", "divided by", "percent of", "square root of", "convert", "to the power of", "into"]):
        res = calculations.calculate(clean)
        if "couldn't" not in res:
            speak(res)
            return True

    # 13. Fun, Games & Easter Eggs
    if "joke" in clean or "make me laugh" in clean:
        speak(fun_easter_eggs.tell_joke())
        return True

    if "fact" in clean:
        speak(fun_easter_eggs.tell_fact())
        return True

    if "flip a coin" in clean or "coin flip" in clean or "flip coin" in clean or "heads or tails" in clean:
        speak(fun_easter_eggs.flip_coin())
        return True

    if "roll a dice" in clean or "roll a die" in clean or "roll dice" in clean or "roll die" in clean:
        speak(fun_easter_eggs.roll_dice())
        return True

    egg_reply = fun_easter_eggs.check_easter_egg(clean)
    if egg_reply:
        speak(egg_reply)
        return True

    # 14. AI Brain (Conversational Memory - Ollama / Gemini / OpenAI)
    ai_resp = ai_brain.ask_ai(clean)
    if ai_resp:
        speak(ai_resp)
        return True

    # 15. Explicit General Knowledge / Wikipedia / Web Search
    if (
        "wikipedia" in clean
        or any(clean.startswith(prefix) for prefix in [
            "who is ", "who was ", "who were ", "who made ",
            "what is ", "what was ", "what are ", "what were ",
            "where is ", "where was ", "where are ",
            "tell me about ", "explain ", "define "
        ])
    ):
        res = knowledge.search_wikipedia(clean)
        if "couldn't find" not in res:
            speak(res)
            return True

    if clean.startswith("search google for ") or clean.startswith("google ") or clean.startswith("search for "):
        speak(knowledge.google_search(clean))
        return True

    # Default fallback
    confused_responses = [
        "I'm not quite sure how to help with that yet, but I'm constantly learning.",
        "I didn't quite catch that. You can ask me to play music, check the weather, set timers, or read news.",
        "Sorry, I don't understand that command yet. Try asking 'What can you do?' for examples."
    ]
    speak(random.choice(confused_responses))
    return True


def run_follow_up_cycle() -> bool:
    """
    Alexa Follow-Up Mode: Keeps microphone open for 5 seconds to catch follow-up commands
    without repeating the wake word.
    """
    if not config.ENABLE_FOLLOW_UP_MODE or not stt.mic_available:
        return True

    time.sleep(0.3)
    chimes.follow_up_chime()
    print("\033[1;35m🎙️  [Follow-Up Mode] Listening for follow-up...\033[0m")
    
    follow_up_text = stt.listen(timeout=config.FOLLOW_UP_TIMEOUT, phrase_time_limit=6)
    if not follow_up_text:
        return True

    # Exit keywords in follow up
    if any(follow_up_text == w or follow_up_text.startswith(w + " ") for w in ["thank you", "thanks", "that's all", "nothing", "stop", "no thanks"]):
        speak("You're welcome!")
        return True

    print(f"\033[1;33mFollow-up query:\033[0m {follow_up_text}")
    has_wake, cmd = extract_wake_word_query(follow_up_text)
    query_to_run = cmd if has_wake else follow_up_text
    
    return execute_intent(query_to_run)


def run_text_mode():
    """Runs assistant in interactive keyboard text mode."""
    display_welcome_banner()
    print("\033[1;32m[Interactive Text Mode Active]\033[0m (Type your command or 'exit' to quit)\n")
    wish_me()

    while True:
        try:
            user_input = input("\n\033[1;33mYou:\033[0m ").strip()
            if not user_input:
                continue

            has_wake, cmd = extract_wake_word_query(user_input)
            query_to_run = cmd if has_wake else user_input

            if has_wake and not cmd:
                speak("Yes? How can I help?")
                continue

            should_continue = execute_intent(query_to_run)
            if not should_continue:
                break
        except (KeyboardInterrupt, EOFError):
            print("\n\033[1;36mJarvis:\033[0m Goodbye!")
            break


def run_voice_mode(continuous_listen=False, allow_text_fallback=True):
    """Runs assistant with microphone voice input and wake word detection."""
    display_welcome_banner()

    if not stt.mic_available:
        print("\033[33m⚠️  Microphone or PyAudio not detected on this system.\033[0m")
        if allow_text_fallback:
            print("\033[32m💡 Falling back to Interactive Text Mode...\033[0m")
            print("To enable microphone, install PyAudio:")
            if CURRENT_OS == "darwin":
                print("  • macOS: brew install portaudio && pip install pyaudio")
            elif CURRENT_OS == "linux":
                print("  • Linux: sudo apt-get install python3-pyaudio")
            else:
                print("  • Windows: pip install pyaudio")
            print()
            run_text_mode()
        return

    wish_me()
    print("\n\033[1;32m🎙️  Listening for wake word...\033[0m (Say 'Jarvis' or 'Alexa')")

    while True:
        try:
            if continuous_listen:
                print("\n\033[1;32m🎙️  Listening...\033[0m")
                heard_text = stt.listen(timeout=5, phrase_time_limit=8)
                if not heard_text:
                    continue
                print(f"\033[1;33mYou said:\033[0m {heard_text}")
                should_continue = execute_intent(heard_text)
                if not should_continue:
                    break
                if config.ENABLE_FOLLOW_UP_MODE:
                    run_follow_up_cycle()
            else:
                heard_text = stt.listen(timeout=5, phrase_time_limit=6)
                if not heard_text:
                    continue

                has_wake, cmd = extract_wake_word_query(heard_text)
                if not has_wake:
                    continue

                print(f"\n\033[1;35m⚡ Wake word detected!\033[0m ({heard_text})")
                chimes.wake_chime()

                if cmd:
                    print(f"\033[1;33mCommand:\033[0m {cmd}")
                    should_continue = execute_intent(cmd)
                    if not should_continue:
                        break
                    if config.ENABLE_FOLLOW_UP_MODE:
                        run_follow_up_cycle()
                else:
                    greetings = ["Yes?", "How can I help?", "I'm listening."]
                    prompt = random.choice(greetings)
                    speak(prompt)
                    print("\033[1;32m🎙️  Listening for command...\033[0m")
                    command_text = stt.listen(timeout=5, phrase_time_limit=8)
                    
                    if not command_text:
                        continue

                    print(f"\033[1;33mYou said:\033[0m {command_text}")
                    should_continue = execute_intent(command_text)
                    if not should_continue:
                        break
                    if config.ENABLE_FOLLOW_UP_MODE:
                        run_follow_up_cycle()

                print("\n\033[1;32m🎙️  Listening for wake word...\033[0m (Say 'Jarvis' or 'Alexa')")

        except KeyboardInterrupt:
            print("\n\n\033[1;36mJarvis:\033[0m Goodbye!")
            break
        except Exception:
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="JARVIS / Alexa Cross-Platform Voice Assistant")
    parser.add_argument("-t", "--text", action="store_true", help="Run in interactive text mode (no microphone needed)")
    parser.add_argument("-n", "--no-wake", action="store_true", help="Listen continuously without requiring wake word")
    parser.add_argument("-g", "--gui", action="store_true", help="Launch Echo Show Smart Display Desktop UI")
    args = parser.parse_args()

    if args.gui:
        # Start voice listener in background thread (without terminal stdin takeover) and launch GUI
        if stt.mic_available:
            t = threading.Thread(
                target=run_voice_mode,
                kwargs={"continuous_listen": args.no_wake, "allow_text_fallback": False},
                daemon=True
            )
            t.start()
        from gui import launch_gui
        launch_gui(on_command_cb=execute_intent)
    elif args.text:
        run_text_mode()
    else:
        run_voice_mode(continuous_listen=args.no_wake)


if __name__ == "__main__":
    main()