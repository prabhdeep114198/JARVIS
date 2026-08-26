"""
Multi-Provider AI Brain with Conversational Memory for JARVIS / Alexa.
Supports Local Ollama, Google Gemini, and OpenAI with contextual multi-turn tracking.
"""

import json
import urllib.parse
import urllib.request
import config

# Multi-turn context memory buffer
CONVERSATION_HISTORY = []
MAX_HISTORY_TURNS = 6


def get_system_prompt() -> str:
    return (
        f"You are an intelligent voice assistant named {config.ASSISTANT_NAME}, functioning like Amazon Alexa. "
        f"The user's name is {config.USER_NAME}. "
        "Keep all answers concise, conversational, and direct (1-3 sentences maximum) "
        "so they are pleasant to hear when read aloud. Avoid markdown formatting, bullet lists, or code blocks."
    )


def reset_memory():
    """Clears conversation context memory."""
    global CONVERSATION_HISTORY
    CONVERSATION_HISTORY.clear()


def _query_ollama(prompt: str) -> str:
    """Queries local Ollama instance (100% offline & free)."""
    try:
        url = f"{config.OLLAMA_URL.rstrip('/')}/api/chat"
        messages = [{"role": "system", "content": get_system_prompt()}]
        for turn in CONVERSATION_HISTORY:
            messages.append(turn)
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": config.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.7}
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=8) as resp:
            result = json.loads(resp.read().decode())
            return result.get("message", {}).get("content", "").strip()
    except Exception:
        return ""


def _query_gemini(prompt: str) -> str:
    """Queries Google Gemini API."""
    if not config.GEMINI_API_KEY:
        return ""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"
        
        contents = []
        # Add history
        for turn in CONVERSATION_HISTORY:
            role = "user" if turn["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": turn["content"]}]})
        
        # Add current prompt with system context
        user_text = f"[System Context: {get_system_prompt()}]\n\nUser Question: {prompt}" if not CONVERSATION_HISTORY else prompt
        contents.append({"role": "user", "parts": [{"text": user_text}]})

        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 150
            }
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=7) as resp:
            result = json.loads(resp.read().decode())
            candidates = result.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return ""
    return ""


def _query_openai(prompt: str) -> str:
    """Queries OpenAI API."""
    if not config.OPENAI_API_KEY:
        return ""

    try:
        url = "https://api.openai.com/v1/chat/completions"
        messages = [{"role": "system", "content": get_system_prompt()}]
        for turn in CONVERSATION_HISTORY:
            messages.append(turn)
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": config.OPENAI_MODEL,
            "messages": messages,
            "max_tokens": 150,
            "temperature": 0.7
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.OPENAI_API_KEY}"
            }
        )
        with urllib.request.urlopen(req, timeout=7) as resp:
            result = json.loads(resp.read().decode())
            return result["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""


def ask_ai(prompt: str) -> str:
    """
    Routes query to configured AI provider with conversation memory.
    """
    clean_prompt = prompt.strip()
    if not clean_prompt:
        return ""

    provider = config.AI_PROVIDER.lower()
    answer = ""

    if provider == "ollama":
        answer = _query_ollama(clean_prompt)
    elif provider == "gemini":
        answer = _query_gemini(clean_prompt)
    elif provider == "openai":
        answer = _query_openai(clean_prompt)
    else:
        # Auto mode: try Gemini -> OpenAI -> Ollama
        if config.GEMINI_API_KEY:
            answer = _query_gemini(clean_prompt)
        if not answer and config.OPENAI_API_KEY:
            answer = _query_openai(clean_prompt)
        if not answer:
            answer = _query_ollama(clean_prompt)

    if answer:
        # Update memory buffer
        CONVERSATION_HISTORY.append({"role": "user", "content": clean_prompt})
        CONVERSATION_HISTORY.append({"role": "assistant", "content": answer})
        if len(CONVERSATION_HISTORY) > MAX_HISTORY_TURNS * 2:
            del CONVERSATION_HISTORY[0:2]

    return answer
