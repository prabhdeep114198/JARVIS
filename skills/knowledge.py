"""
General Knowledge, Wikipedia, & AI Brain Skill for JARVIS / Alexa.
Answers general knowledge queries using Wikipedia and optional OpenAI LLM.
"""

import json
import re
import urllib.parse
import urllib.request
import webbrowser
import config

try:
    import wikipedia
    HAS_WIKIPEDIA = True
except ImportError:
    HAS_WIKIPEDIA = False


def _clean_speech_text(text: str) -> str:
    """Cleans text from Wikipedia markup, brackets, citations, and weird phonetics."""
    # Remove citations like [1], [2]
    clean = re.sub(r"\[\d+\]", "", text)
    # Remove parentheses content like (listen; born 1979) if inside parenthesis
    clean = re.sub(r"\([^\)]*\)", "", clean)
    # Remove excessive spaces and newlines
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def search_wikipedia(query: str, sentences: int = 2) -> str:
    """Searches Wikipedia and returns a clean, spoken summary."""
    clean_query = query.strip()
    # Strip common question prefixes
    clean_query = re.sub(
        r"^(?:search\s+wikipedia\s+for|wikipedia|who\s+is|who\s+was|who\s+were|what\s+is|what\s+was|what\s+are|what\s+were|where\s+is|where\s+was|tell\s+me\s+about|explain)\s*",
        "",
        clean_query,
        flags=re.IGNORECASE
    ).strip()

    if not clean_query:
        return "What topic would you like me to look up on Wikipedia?"

    if HAS_WIKIPEDIA:
        try:
            summary = wikipedia.summary(clean_query, sentences=sentences, auto_suggest=True)
            cleaned = _clean_speech_text(summary)
            if cleaned:
                return f"According to Wikipedia: {cleaned}"
        except wikipedia.DisambiguationError as e:
            try:
                # Try the first option in disambiguation
                if e.options:
                    first_opt = e.options[0]
                    summary = wikipedia.summary(first_opt, sentences=sentences)
                    cleaned = _clean_speech_text(summary)
                    return f"According to Wikipedia: {cleaned}"
            except Exception:
                pass
        except Exception:
            pass

    # Fallback to Wikipedia REST API (Zero dependency)
    try:
        wiki_api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_query)}"
        req = urllib.request.Request(
            wiki_api_url,
            headers={"User-Agent": "JarvisAssistant/1.0 (contact@example.com)"}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            extract = data.get("extract")
            if extract:
                cleaned = _clean_speech_text(extract)
                # Take first 2 sentences
                sentences_list = re.split(r'(?<=[.!?])\s+', cleaned)
                short_summary = " ".join(sentences_list[:sentences])
                return f"According to Wikipedia: {short_summary}"
    except Exception:
        pass

    return f"I couldn't find a Wikipedia page for {clean_query}."


def ask_ai_brain(prompt: str) -> str:
    """Queries OpenAI or conversational model if API key is provided."""
    if not config.OPENAI_API_KEY:
        return ""

    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.OPENAI_API_KEY}"
        }
        body = {
            "model": config.OPENAI_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an Alexa-like voice assistant named Jarvis. "
                        "Keep your responses concise, natural, and friendly (1-3 sentences max) "
                        "so they sound great when read aloud."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=6) as response:
            res_data = json.loads(response.read().decode())
            reply = res_data["choices"][0]["message"]["content"].strip()
            return reply
    except Exception:
        return ""


def google_search(query: str) -> str:
    """Performs a Google web search and opens the browser."""
    clean = query.strip()
    for phrase in ["google search for", "google", "search for", "search"]:
        clean = clean.replace(phrase, "")
    clean = clean.strip()
    
    url = f"https://www.google.com/search?q={urllib.parse.quote(clean)}"
    webbrowser.open(url)
    return f"Here are the Google search results for {clean}."
