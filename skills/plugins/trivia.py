"""
Interactive Trivia & Quiz Game Plugin for JARVIS / Alexa.
Fetches general knowledge trivia questions from Open Trivia DB.
"""

import html
import json
import random
import urllib.request

COMMAND_KEYWORDS = [
    "trivia",
    "quiz",
    "ask me a question",
    "trivia question",
    "play trivia"
]
DESCRIPTION = "Interactive Trivia & General Knowledge Quiz"

OFFLINE_TRIVIA = [
    ("What planet is known as the Red Planet?", "Mars"),
    ("What is the chemical symbol for gold?", "Au"),
    ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
    ("How many continents are there on Earth?", "Seven"),
    ("What is the largest mammal in the world?", "The Blue Whale"),
    ("In what year did the Titanic sink?", "1912")
]


def get_trivia_question() -> str:
    """Fetches a random trivia question."""
    try:
        url = "https://opentdb.com/api.php?amount=1&type=multiple"
        req = urllib.request.Request(url, headers={"User-Agent": "JarvisAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            if data.get("results"):
                item = data["results"][0]
                question = html.unescape(item["question"])
                correct = html.unescape(item["correct_answer"])
                return f"Here is your trivia question: {question} ... The answer is: {correct}!"
    except Exception:
        pass

    q, a = random.choice(OFFLINE_TRIVIA)
    return f"Here is your trivia question: {q} ... The answer is: {a}!"


def handle(query: str) -> str:
    return get_trivia_question()
