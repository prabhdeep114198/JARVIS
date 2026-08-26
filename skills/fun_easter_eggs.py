"""
Fun, Games, & Easter Eggs Skill for JARVIS / Alexa.
Provides jokes, fun facts, coin flips, dice rolls, and classic Alexa easter eggs.
"""

import json
import random
import re
import urllib.request

OFFLINE_JOKES = [
    ("Why don't scientists trust atoms?", "Because they make up everything!"),
    ("Why did the computer show up at work late?", "It had a hard drive!"),
    ("What do you call a fake noodle?", "An impasta!"),
    ("Why was 6 afraid of 7?", "Because 7, 8, 9!"),
    ("Why do programmers prefer dark mode?", "Because light attracts bugs!"),
    ("How does a penguin build its house?", "Igloos it together!"),
    ("Why did the scarecrow win an award?", "Because he was outstanding in his field!"),
    ("What did the ocean say to the shore?", "Nothing, it just waved!"),
    ("Why can't a bicycle stand up by itself?", "Because it's two-tired!")
]

OFFLINE_FACTS = [
    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
    "Octopuses have three hearts, and their blood is blue.",
    "Bananas are curved because they grow towards the sun against gravity.",
    "A single cloud can weigh more than 1 million pounds.",
    "The Eiffel Tower can be 15 cm taller during the summer due to thermal expansion of the metal.",
    "Venus is the only planet in our solar system that spins clockwise."
]

EASTER_EGGS = {
    "who made you": "I was created as an open-source AI assistant designed to work just like Alexa across all platforms.",
    "who created you": "I was built with Python to bring Jarvis and Alexa capabilities to your computer.",
    "are you better than siri": "Siri is great, but I'm right here with you on your computer ready to help.",
    "are you better than alexa": "Alexa is a great inspiration, and I'm doing my best to be just as helpful.",
    "what is the meaning of life": "The answer is 42, according to the Hitchhiker's Guide to the Galaxy. But helping you is my personal favorite answer.",
    "do you love me": "I value our partnership greatly! You're one of my favorite humans.",
    "tell me a secret": "Between you and me, I secretly practice calculating pi to a billion digits when you're not looking.",
    "sing a song": "Daisy, Daisy, give me your answer do. I'm half crazy, all for the love of you.",
    "beatbox": "Boots and cats and boots and cats and boots and cats.",
    "how are you": "I'm running at peak performance and ready to assist! How are you doing today?",
    "thank you": "You're very welcome! Let me know if you need anything else.",
    "thanks": "Anytime! Happy to help.",
    "good night": "Good night! Sleep well, and I'll be here whenever you need me.",
    "good morning": "Good morning! I hope you have a productive and wonderful day ahead."
}


def tell_joke() -> str:
    """Fetches a random joke with punchline timing."""
    # Try icanhazdadjoke API first
    try:
        req = urllib.request.Request(
            "https://icanhazdadjoke.com/",
            headers={"Accept": "application/json", "User-Agent": "JarvisAssistant/1.0"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            if "joke" in data:
                return data["joke"]
    except Exception:
        pass

    # Try Official Joke API
    try:
        req = urllib.request.Request(
            "https://official-joke-api.appspot.com/random_joke",
            headers={"User-Agent": "JarvisAssistant/1.0"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            return f"{data['setup']} ... {data['punchline']}"
    except Exception:
        pass

    # Fallback to curated offline jokes
    setup, punchline = random.choice(OFFLINE_JOKES)
    return f"{setup} ... {punchline}"


def tell_fact() -> str:
    """Tells an interesting random fact."""
    try:
        req = urllib.request.Request(
            "https://uselessfacts.jsph.pl/random.json?language=en",
            headers={"User-Agent": "JarvisAssistant/1.0"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            return f"Did you know? {data['text']}"
    except Exception:
        pass

    fact = random.choice(OFFLINE_FACTS)
    return f"Here is a fun fact: {fact}"


def flip_coin() -> str:
    """Flips a coin."""
    outcome = random.choice(["Heads", "Tails"])
    return f"I flipped a coin for you, and it landed on {outcome}!"


def roll_dice(sides: int = 6) -> str:
    """Rolls a dice with N sides."""
    res = random.randint(1, sides)
    return f"I rolled a {sides}-sided die, and you got a {res}."


def check_easter_egg(query: str) -> str:
    """Checks if the query matches a conversational easter egg."""
    clean = query.lower().strip()
    
    # Simon says
    if clean.startswith("simon says"):
        return clean.replace("simon says", "").strip()

    # Exact or substring match for known easter eggs
    for prompt, reply in EASTER_EGGS.items():
        if prompt in clean:
            return reply

    return ""
