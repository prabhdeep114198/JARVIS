"""
Media & Music Skill for JARVIS / Alexa.
Cross-platform media playback for YouTube, Spotify, and popular web services.
Directly fetches the top YouTube video ID and autoplays the video in your browser.
"""

import re
import urllib.parse
import urllib.request
import webbrowser

POPULAR_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "spotify": "https://open.spotify.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.com",
    "github": "https://www.github.com",
    "reddit": "https://www.reddit.com",
    "twitter": "https://www.x.com",
    "x": "https://www.x.com",
    "instagram": "https://www.instagram.com",
    "wikipedia": "https://www.wikipedia.org",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chat.openai.com"
}


def _get_direct_youtube_url(query: str) -> str:
    """
    Queries YouTube search and extracts the exact video URL of the top result
    to ensure immediate playback rather than showing search results.
    """
    clean = query.strip()
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(clean)}"
    
    try:
        req = urllib.request.Request(
            search_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode("utf-8", errors="ignore")
            # Find first valid 11-character video ID
            video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)
            if video_ids:
                # Return direct video link with autoplay
                return f"https://www.youtube.com/watch?v={video_ids[0]}"
    except Exception:
        pass

    # Fallback to search query URL if parsing fails
    return search_url


def play_music(query: str) -> str:
    """Directly finds and plays music or videos on YouTube / Spotify."""
    clean_query = query.strip()
    for prefix in ["play ", "can you play ", "please play ", "on youtube", "song "]:
        clean_query = clean_query.replace(prefix, "").strip()

    if not clean_query:
        return "What would you like me to play?"

    # Check if Spotify is specifically requested
    if "on spotify" in query.lower():
        song_name = clean_query.replace("on spotify", "").strip()
        spotify_url = f"https://open.spotify.com/search/{urllib.parse.quote(song_name)}"
        webbrowser.open(spotify_url)
        return f"Playing {song_name} on Spotify."

    # Direct YouTube video playback
    video_url = _get_direct_youtube_url(clean_query)
    webbrowser.open(video_url)
    return f"Playing {clean_query} on YouTube."


def open_website(site_query: str) -> str:
    """Opens a website in the default browser."""
    target = site_query.lower().strip()
    
    # Check popular predefined sites
    for key, url in POPULAR_SITES.items():
        if key in target:
            webbrowser.open(url)
            return f"Opening {key.capitalize()}."

    # Check if a custom domain was requested
    if not target.startswith("http://") and not target.startswith("https://"):
        if "." in target:
            target_url = f"https://{target}"
        else:
            target_url = f"https://www.google.com/search?q={urllib.parse.quote(site_query)}"
    else:
        target_url = target

    webbrowser.open(target_url)
    return f"Opening {site_query}."
