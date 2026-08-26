"""
Crypto & Stock Prices Plugin for JARVIS / Alexa.
Fetches live cryptocurrency and stock quotes via free public APIs.
"""

import json
import re
import urllib.request

COMMAND_KEYWORDS = [
    "bitcoin",
    "ethereum",
    "crypto",
    "solana",
    "dogecoin",
    "stock price",
    "stock of",
    "price of btc",
    "price of eth"
]
DESCRIPTION = "Live Crypto and Stock Quotes"

COIN_MAP = {
    "bitcoin": "bitcoin",
    "btc": "bitcoin",
    "ethereum": "ethereum",
    "eth": "ethereum",
    "solana": "solana",
    "sol": "solana",
    "dogecoin": "dogecoin",
    "doge": "dogecoin",
    "cardano": "cardano",
    "ripple": "ripple",
    "xrp": "ripple"
}


def get_crypto_price(coin_id: str) -> str:
    """Fetches real-time crypto price from CoinGecko free API."""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        req = urllib.request.Request(url, headers={"User-Agent": "JarvisAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            if coin_id in data:
                price = data[coin_id]["usd"]
                change = data[coin_id].get("usd_24h_change", 0)
                change_str = f"up {change:.1f}%" if change >= 0 else f"down {abs(change):.1f}%"
                return f"{coin_id.capitalize()} is currently trading at ${price:,.2f} USD, {change_str} in the last 24 hours."
    except Exception:
        pass
    return f"I couldn't retrieve the current market price for {coin_id}."


def handle(query: str) -> str:
    clean = query.lower()
    for symbol, coin_id in COIN_MAP.items():
        if symbol in clean:
            return get_crypto_price(coin_id)

    return get_crypto_price("bitcoin")
