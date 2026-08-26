"""
Timer & Alarm Skill for JARVIS / Alexa.
Provides background timers, alarms, status inquiries, and audio alarms
just like Amazon Alexa.
"""

import re
import threading
import time
from typing import Dict, Optional

# Active timers dict: {timer_id: {"name": str, "duration": int, "end_time": float, "thread": Thread, "cancelled": bool}}
ACTIVE_TIMERS: Dict[int, dict] = {}
TIMER_COUNTER = 1


def parse_time_duration(query: str) -> Optional[int]:
    """
    Parses natural language duration into total seconds.
    Examples: '10 minutes', '1 minute 30 seconds', '45 seconds', '2 hours'.
    """
    total_seconds = 0
    clean = query.lower()

    hours_match = re.search(r"(\d+)\s*(?:hour|hours|hr|hrs)", clean)
    if hours_match:
        total_seconds += int(hours_match.group(1)) * 3600

    mins_match = re.search(r"(\d+)\s*(?:minute|minutes|min|mins)", clean)
    if mins_match:
        total_seconds += int(mins_match.group(1)) * 60

    secs_match = re.search(r"(\d+)\s*(?:second|seconds|sec|secs)", clean)
    if secs_match:
        total_seconds += int(secs_match.group(1))

    # If just a number followed by nothing else (e.g. "set a timer for 5") -> assume minutes or seconds if small
    if total_seconds == 0:
        num_match = re.search(r"timer\s+(?:for\s+)?(\d+)", clean)
        if num_match:
            val = int(num_match.group(1))
            total_seconds = val * 60 if val <= 60 else val

    return total_seconds if total_seconds > 0 else None


def format_duration(seconds: int) -> str:
    """Converts seconds into human-readable duration."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    parts = []
    if h > 0:
        parts.append(f"{h} hour" if h == 1 else f"{h} hours")
    if m > 0:
        parts.append(f"{m} minute" if m == 1 else f"{m} minutes")
    if s > 0:
        parts.append(f"{s} second" if s == 1 else f"{s} seconds")

    return " and ".join(parts) if parts else "0 seconds"


def _run_timer_thread(timer_id: int, label: str, duration_sec: int, on_complete_cb):
    """Background worker that waits for the timer duration and triggers alarm."""
    time.sleep(duration_sec)
    
    timer = ACTIVE_TIMERS.get(timer_id)
    if timer and not timer.get("cancelled", False):
        ACTIVE_TIMERS.pop(timer_id, None)
        # Trigger alarm callback
        if on_complete_cb:
            on_complete_cb(label, duration_sec)


def set_timer(query: str, on_complete_cb=None) -> str:
    """Sets a background countdown timer."""
    global TIMER_COUNTER

    duration_sec = parse_time_duration(query)
    if not duration_sec:
        return "How long would you like the timer for?"

    # Extract optional label (e.g. "timer for pizza", "timer for tea")
    label_match = re.search(r"timer\s+(?:for\s+)?(?:\d+\s*(?:hours?|hrs?|minutes?|mins?|seconds?|secs?)\s*)?(?:for\s+|called\s+)([\w\s]+)", query.lower())
    label = label_match.group(1).strip() if label_match else None

    timer_id = TIMER_COUNTER
    TIMER_COUNTER += 1

    dur_str = format_duration(duration_sec)
    timer_name = label if label else f"{dur_str} timer"

    end_time = time.time() + duration_sec
    timer_data = {
        "id": timer_id,
        "name": timer_name,
        "duration": duration_sec,
        "end_time": end_time,
        "cancelled": False
    }

    t = threading.Thread(
        target=_run_timer_thread,
        args=(timer_id, timer_name, duration_sec, on_complete_cb),
        daemon=True
    )
    timer_data["thread"] = t
    ACTIVE_TIMERS[timer_id] = timer_data
    t.start()

    return f"{timer_name.capitalize()} set for {dur_str}."


def get_timers_status() -> str:
    """Returns the remaining time of all active timers."""
    now = time.time()
    active = [t for t in ACTIVE_TIMERS.values() if not t["cancelled"] and t["end_time"] > now]

    if not active:
        return "You have no active timers."

    if len(active) == 1:
        t = active[0]
        remaining = int(t["end_time"] - now)
        return f"There is {format_duration(remaining)} left on your {t['name']}."

    reports = []
    for t in active:
        remaining = int(t["end_time"] - now)
        reports.append(f"{t['name']} with {format_duration(remaining)} remaining")

    return f"You have {len(active)} active timers: " + ", ".join(reports) + "."


def cancel_timer() -> str:
    """Cancels active timers."""
    if not ACTIVE_TIMERS:
        return "You have no active timers to cancel."

    count = len(ACTIVE_TIMERS)
    for t in ACTIVE_TIMERS.values():
        t["cancelled"] = True
    ACTIVE_TIMERS.clear()

    return f"Cancelled {count} timer." if count == 1 else f"Cancelled all {count} timers."
