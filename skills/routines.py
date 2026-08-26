"""
Alexa-Style Routines & Automation Engine for JARVIS / Alexa.
Executes multi-step automated workflows with a single voice command.
"""

import datetime
import time
import config
from audio_engine import speak
from skills import media, news, notes_reminders, system_control, timer_alarm, weather


def run_good_morning_routine():
    """Executes the complete Good Morning / Start My Day routine."""
    hour = datetime.datetime.now().hour
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    date_str = datetime.datetime.now().strftime("%A, %B %d")

    # 1. Greeting
    speak(f"Good morning, {config.USER_NAME}! It's {time_str} on {date_str}.")

    # 2. Weather
    weather_report = weather.get_weather()
    speak(weather_report)

    # 3. Reminders & Tasks
    reminders = notes_reminders.get_reminders()
    if "no saved reminders" not in reminders.lower():
        speak("Here are your agenda items for today:")
        speak(reminders)

    # 4. Top News Headlines
    news_brief = news.get_news_headlines(count=3)
    speak("Here is your morning flash briefing:")
    speak(news_brief)

    speak(f"You're all set, {config.USER_NAME}. Have a wonderful and productive day!")


def run_good_night_routine():
    """Executes the Bedtime / Good Night routine."""
    speak(f"Good night, {config.USER_NAME}!")
    
    # Check reminders
    reminders = notes_reminders.get_reminders()
    if "no saved reminders" not in reminders.lower():
        speak(f"Just a quick reminder for tomorrow: {reminders}")

    # Set night volume
    system_control.control_volume("set", level=25)
    speak("I have adjusted your volume to a relaxing level. Sleep well!", whisper=True)


def run_focus_mode_routine(on_timer_complete=None):
    """Executes Focus / Coding Mode routine (Work + Pomodoro + Lo-Fi)."""
    speak(f"Activating Focus Mode for {config.USER_NAME}.")
    
    # Launch developer tools
    system_control.open_application("vscode")
    
    # Start 25-minute Pomodoro timer
    timer_alarm.set_timer("timer for 25 minutes for focus session", on_complete_cb=on_timer_complete)
    
    # Start Lo-Fi focus music
    media.play_music("lofi hip hop radio study relax")
    
    speak("VS Code launched, Lo-Fi music playing, and a 25 minute focus timer is ticking. Happy coding!")


def run_relax_mode_routine():
    """Executes Relax / Movie Time routine."""
    speak("Relaxation mode activated. Let's unwind.")
    media.open_website("netflix")
    system_control.control_volume("set", level=45)


def check_and_execute_routine(query: str, on_timer_complete=None) -> bool:
    """Checks if query matches a predefined routine and runs it."""
    clean = query.lower().strip()

    if any(p in clean for p in ["start my day", "good morning routine", "morning routine", "morning briefing"]):
        run_good_morning_routine()
        return True

    if any(p in clean for p in ["bedtime routine", "good night routine", "sleep routine", "going to sleep"]):
        run_good_night_routine()
        return True

    if any(p in clean for p in ["focus mode", "coding mode", "work mode", "study mode", "pomodoro mode"]):
        run_focus_mode_routine(on_timer_complete=on_timer_complete)
        return True

    if any(p in clean for p in ["relax mode", "movie mode", "movie time", "chill mode"]):
        run_relax_mode_routine()
        return True

    return False
