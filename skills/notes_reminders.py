"""
Notes & Reminders Skill for JARVIS / Alexa.
Stores persistent notes, to-dos, and reminders in JSON format.
"""

import datetime
import json
import os
import config


def _load_data() -> dict:
    """Loads stored data from the JSON file."""
    if not os.path.exists(config.DATA_FILE):
        return {"reminders": [], "notes": []}
    try:
        with open(config.DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"reminders": [], "notes": []}


def _save_data(data: dict):
    """Saves updated data to the JSON file."""
    try:
        with open(config.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving data: {e}")


def add_reminder(reminder_text: str) -> str:
    """Adds a new reminder."""
    clean = reminder_text.strip()
    if not clean:
        return "What would you like me to remind you about?"

    data = _load_data()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    data.setdefault("reminders", []).append({
        "text": clean,
        "created_at": timestamp
    })
    _save_data(data)
    return f"I've saved your reminder: {clean}."


def get_reminders() -> str:
    """Reads all saved reminders."""
    data = _load_data()
    reminders = data.get("reminders", [])

    if not reminders:
        return "You have no saved reminders."

    if len(reminders) == 1:
        return f"You have 1 reminder: {reminders[0]['text']}."

    msg = f"You have {len(reminders)} reminders: "
    items = [f"Number {i+1}: {r['text']}" for i, r in enumerate(reminders)]
    return msg + ". ".join(items) + "."


def clear_reminders() -> str:
    """Clears all saved reminders."""
    data = _load_data()
    count = len(data.get("reminders", []))
    data["reminders"] = []
    _save_data(data)
    if count == 0:
        return "You have no reminders to clear."
    return f"Cleared {count} reminder{'s' if count > 1 else ''}."


def add_note(note_text: str) -> str:
    """Adds a new note."""
    clean = note_text.strip()
    if not clean:
        return "What note would you like me to take?"

    data = _load_data()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    data.setdefault("notes", []).append({
        "text": clean,
        "created_at": timestamp
    })
    _save_data(data)
    return f"I've recorded that in your notes: {clean}."


def get_notes() -> str:
    """Reads all saved notes."""
    data = _load_data()
    notes = data.get("notes", [])

    if not notes:
        return "You have no saved notes."

    if len(notes) == 1:
        return f"Here is your note: {notes[0]['text']}."

    msg = f"You have {len(notes)} notes: "
    items = [f"Note {i+1}: {n['text']}" for i, n in enumerate(notes)]
    return msg + ". ".join(items) + "."


def clear_notes() -> str:
    """Clears all saved notes."""
    data = _load_data()
    count = len(data.get("notes", []))
    data["notes"] = []
    _save_data(data)
    if count == 0:
        return "You have no notes to clear."
    return f"Cleared {count} note{'s' if count > 1 else ''}."
