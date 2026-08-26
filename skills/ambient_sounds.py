"""
Ambient Sleep Sounds & Live Internet Radio Skill for JARVIS / Alexa.
Plays relaxing sleep soundscapes (Rain, Ocean, Fireplace, White Noise)
and live streaming radio stations.
"""

import webbrowser

AMBIENT_SOUNDS = {
    "rain": "https://www.youtube.com/watch?v=mPZkdNFkNps",
    "ocean": "https://www.youtube.com/watch?v=bn9F19Hi1Lk",
    "fireplace": "https://www.youtube.com/watch?v=L_LUpnjgPso",
    "thunderstorm": "https://www.youtube.com/watch?v=s70O4qC1oA4",
    "forest": "https://www.youtube.com/watch?v=xNN7iTA57jM",
    "white noise": "https://www.youtube.com/watch?v=nMfPqeZjc2c",
    "lofi": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
    "jazz": "https://www.youtube.com/watch?v=Dx5qFachd3A",
    "piano": "https://www.youtube.com/watch?v=77ZozI0rw7w"
}


def play_ambient_sound(sound_type: str) -> str:
    """Plays relaxing ambient sleep sounds or music."""
    clean = sound_type.lower().strip()
    
    target_key = None
    for key in AMBIENT_SOUNDS:
        if key in clean:
            target_key = key
            break

    if target_key:
        url = AMBIENT_SOUNDS[target_key]
        webbrowser.open(url)
        return f"Playing {target_key} sounds for relaxation."

    # Generic ambient sound search
    webbrowser.open(f"https://www.youtube.com/results?search_query={sound_type}+sounds+relaxing")
    return f"Playing {sound_type} sounds."


def check_ambient_sound_query(query: str) -> str:
    """Checks if voice query is requesting ambient sleep sounds."""
    clean = query.lower().strip()
    
    if any(k in clean for k in ["rain sounds", "ocean waves", "fireplace sounds", "white noise", "sleep sounds", "nature sounds", "thunderstorm sounds", "relaxing sounds", "ambient sounds"]):
        for key in AMBIENT_SOUNDS:
            if key in clean:
                return play_ambient_sound(key)
        return play_ambient_sound("rain")

    return ""
