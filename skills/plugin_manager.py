"""
Modular Plugin Manager for JARVIS / Alexa.
Dynamically discovers and loads external voice skill plugins from skills/plugins/.
"""

import importlib.util
import os
from typing import Callable, Dict, List
import config

LOADED_PLUGINS: List[dict] = []


def load_plugins():
    """Scans and loads all plugins from config.PLUGINS_DIR."""
    global LOADED_PLUGINS
    LOADED_PLUGINS.clear()

    if not os.path.exists(config.PLUGINS_DIR):
        os.makedirs(config.PLUGINS_DIR, exist_ok=True)

    for filename in os.listdir(config.PLUGINS_DIR):
        if filename.endswith(".py") and not filename.startswith("__"):
            plugin_path = os.path.join(config.PLUGINS_DIR, filename)
            module_name = filename[:-3]

            try:
                spec = importlib.util.spec_from_file_location(module_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check if module exposes required plugin attributes
                keywords = getattr(module, "COMMAND_KEYWORDS", [])
                handle_fn = getattr(module, "handle", None)

                if callable(handle_fn) and keywords:
                    LOADED_PLUGINS.append({
                        "name": module_name,
                        "keywords": [k.lower() for k in keywords],
                        "handle": handle_fn,
                        "description": getattr(module, "DESCRIPTION", "Custom Skill Plugin")
                    })
            except Exception as e:
                print(f"\033[33m[Warning: Failed to load plugin '{filename}': {e}]\033[0m")


def dispatch_plugin(query: str) -> str:
    """Checks if query matches any loaded plugin and returns response."""
    clean = query.lower().strip()

    for plugin in LOADED_PLUGINS:
        for keyword in plugin["keywords"]:
            if keyword in clean:
                try:
                    return plugin["handle"](query)
                except Exception as e:
                    return f"Error executing {plugin['name']} plugin."

    return ""


# Initialize on import
load_plugins()
