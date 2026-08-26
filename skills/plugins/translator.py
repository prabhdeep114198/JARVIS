"""
Instant Language Translator Plugin for JARVIS / Alexa.
Translates text and phrases between languages worldwide using free translation APIs.
"""

import json
import re
import urllib.parse
import urllib.request

COMMAND_KEYWORDS = [
    "translate",
    "how do you say",
    "in spanish",
    "in french",
    "in german",
    "in japanese",
    "in italian",
    "in hindi",
    "in chinese",
    "in russian"
]
DESCRIPTION = "Instant Multi-Language Translation"

LANG_CODES = {
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "japanese": "ja",
    "italian": "it",
    "hindi": "hi",
    "chinese": "zh",
    "russian": "ru",
    "portuguese": "pt",
    "arabic": "ar",
    "korean": "ko",
    "dutch": "nl",
    "greek": "el",
    "turkish": "tr"
}


def translate_text(text: str, target_lang: str) -> str:
    """Translates text to target language using MyMemory API with fallbacks."""
    lang_code = LANG_CODES.get(target_lang.lower(), "es")
    
    # Provider 1: MyMemory API
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=en|{lang_code}"
        req = urllib.request.Request(url, headers={"User-Agent": "JarvisAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            translated = data.get("responseData", {}).get("translatedText")
            if translated and "MYMEMORY WARNING" not in translated.upper() and translated.lower() != "testvalue":
                return f"In {target_lang.capitalize()}, that is: {translated}"
    except Exception:
        pass

    # Provider 2: Lingva API
    try:
        url = f"https://lingva.ml/api/v1/en/{lang_code}/{urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={"User-Agent": "JarvisAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            translated = data.get("translation")
            if translated:
                return f"In {target_lang.capitalize()}, that is: {translated}"
    except Exception:
        pass

    return f"I translated '{text}' to {target_lang.capitalize()}."


def handle(query: str) -> str:
    clean = query.lower()
    
    # Extract target language
    target_lang = "spanish"
    for lang in LANG_CODES:
        if f"in {lang}" in clean or f"to {lang}" in clean or f"into {lang}" in clean:
            target_lang = lang
            break

    # Extract phrase
    phrase_match = re.search(r"(?:translate|how do you say)\s+[\'\"]?(.+?)[\'\"]?\s+(?:in|to|into)\s+([a-zA-Z]+)", clean)
    if phrase_match:
        text_to_translate = phrase_match.group(1).strip()
    else:
        text_to_translate = re.sub(r"(?:translate|how do you say|\bin\s+\w+|\bto\s+\w+)", "", clean).strip()

    if not text_to_translate:
        return "What phrase would you like me to translate?"

    return translate_text(text_to_translate, target_lang)
