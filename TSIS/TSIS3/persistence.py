"""
persistence.py  —  TSIS 3
Handles saving and loading data to/from JSON files on disk.
Two types of data are managed:
  1. Leaderboard  — top-10 player scores stored in leaderboard.json
  2. Settings     — user preferences stored in settings.json
"""

import json   # Standard library for reading/writing JSON files
import os     # Used to check whether a file exists before opening it

# ── File paths ───────────────────────────────────────────────────────────────
LEADERBOARD_FILE = "leaderboard.json"   # File that stores the top-10 high scores
SETTINGS_FILE    = "settings.json"      # File that stores user preferences

# Default values used if settings.json doesn't exist or is missing a key
DEFAULT_SETTINGS = {
    "sound":       False,    # Sound effects off by default
    "car_color":   "blue",   # Default player car color
    "difficulty":  "normal", # "easy" | "normal" | "hard"
    "username":    "",       # Empty username prompts the player to enter one
}



# LEADERBOARD  functions


def load_leaderboard():
    """
    Read leaderboard.json from disk and return it as a list of dicts.
    Returns an empty list if the file doesn't exist or is malformed.
    """
    if not os.path.exists(LEADERBOARD_FILE):
        return []   # File not found → fresh start with no scores
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)   # Parse JSON into a Python list
        return data if isinstance(data, list) else []   # Safety check: must be a list
    except Exception:
        return []   # Any read/parse error → return empty rather than crash


def save_leaderboard(entries: list):
    """
    Sort all entries by score (highest first), keep only the top 10,
    then write the result back to leaderboard.json.
    """
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)   # Sort descending by score
    top = entries[:10]   # Keep only the best 10 entries
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(top, f, ensure_ascii=False, indent=2)   # Pretty-print JSON with 2-space indent


def add_leaderboard_entry(username: str, score: int, distance: int, coins: int):
    """
    Add or update a player's best score in the leaderboard.

    Rules:
    - If an entry with the same username already exists:
        * Replace it only if the new score is HIGHER than the saved one.
        * Otherwise do nothing (don't downgrade a player's record).
    - If the username is not yet on the board, append a new entry.

    The leaderboard is always trimmed to the top 10 inside save_leaderboard().
    """
    entries = load_leaderboard()
    new_entry = {"name": username, "score": score, "distance": distance, "coins": coins}

    for i, e in enumerate(entries):
        if e.get("name", "").lower() == username.lower():   # Case-insensitive name match
            if score > e.get("score", 0):
                entries[i] = new_entry      # Replace old record with the better one
                save_leaderboard(entries)   # Save immediately
            return   # Either updated or score was worse — stop here in both cases

    # Username not found in the list → add as a new entry
    entries.append(new_entry)
    save_leaderboard(entries)



# SETTINGS  functions


def load_settings() -> dict:
    """
    Read settings.json from disk and return a complete settings dict.
    - If the file doesn't exist → returns a copy of DEFAULT_SETTINGS.
    - If the file exists but is missing some keys → fills them from DEFAULT_SETTINGS.
    - Any unknown keys from the file are ignored (only known keys are used).
    """
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()   # No file yet → use defaults
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = DEFAULT_SETTINGS.copy()   # Start with all defaults
        # Overwrite only the keys that are recognised (prevents injecting unknown keys)
        result.update({k: v for k, v in data.items() if k in DEFAULT_SETTINGS})
        return result
    except Exception:
        return DEFAULT_SETTINGS.copy()   # File corrupted → fall back to defaults


def save_settings(settings: dict):
    """Write the current settings dict to settings.json."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)   # Human-readable JSON