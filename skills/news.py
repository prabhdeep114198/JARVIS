"""
News Flash Briefing Skill for JARVIS / Alexa.
Fetches top world, tech, and business headlines from RSS feeds with zero dependencies.
"""

import urllib.request
import xml.etree.ElementTree as ET
import config


def get_news_headlines(category: str = "top", count: int = 4) -> str:
    """Fetches and summarizes top news headlines."""
    feed_url = config.NEWS_FEEDS.get(category.lower(), config.NEWS_FEEDS["top"])

    try:
        req = urllib.request.Request(
            feed_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        items = root.findall(".//item")
        
        if not items:
            return "I couldn't find any news articles right now."

        headlines = []
        for item in items[:count]:
            title = item.find("title")
            if title is not None and title.text:
                clean_title = title.text.strip()
                # Remove common source suffixes if present
                clean_title = clean_title.split(" - ")[0]
                headlines.append(clean_title)

        if not headlines:
            return "No news headlines were available."

        ordinal_words = ["First", "Second", "Third", "Fourth", "Fifth"]
        formatted_list = []
        for i, h in enumerate(headlines):
            ord_word = ordinal_words[i] if i < len(ordinal_words) else f"Number {i+1}"
            formatted_list.append(f"{ord_word}: {h}")

        intro = f"Here are the latest {category if category != 'top' else ''} headlines: "
        return intro + ". ".join(formatted_list) + "."

    except Exception:
        return "Sorry, I was unable to connect to the news feed. Please check your internet connection."
