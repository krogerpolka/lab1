"""
sounds.py  —  TSIS 3
Loads sound effects from assets/sounds/*.wav and provides
a simple API for the rest of the game to play them.
"""

import pygame   # pygame.mixer handles audio playback
import os       # os.path.join builds cross-platform file paths

# Pre-initialize the mixer BEFORE pygame.init() is called elsewhere.
# This sets audio quality: 44100 Hz sample rate, 16-bit signed, mono, 512-sample buffer.
# A small buffer (512) reduces audio latency, which is important for responsive sound effects.
pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
pygame.mixer.init()   # Activate the mixer so sounds can be loaded and played

# Directory containing all .wav sound files
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "assets", "sounds")

# Maps sound names (used in code) → their .wav filenames on disk
SOUND_FILES = {
    "coin":         "coin.wav",         # Played when collecting a bronze or silver coin
    "gold_coin":    "gold_coin.wav",    # Played when collecting the rare gold coin
    "crash":        "crash.wav",        # Played when the player is killed (enemy or obstacle)
    "nitro":        "nitro.wav",        # Played when nitro activates
    "shield":       "shield.wav",       # Played when shield activates or absorbs a hit
    "powerup":      "powerup.wav",      # Generic sound for the repair power-up
    "obstacle_hit": "obstacle_hit.wav", # Played when an obstacle hits but doesn't kill (damage taken)
    "engine":       "engine.wav",       # Looped continuously during gameplay as background engine noise
}

# Volume levels for each sound (0.0 = silent, 1.0 = maximum)
# Set individually so no single effect dominates the mix
VOLUMES = {
    "coin":         0.6,
    "gold_coin":    0.7,
    "crash":        0.9,    # Crash is the most important — loudest
    "nitro":        0.7,
    "shield":       0.6,
    "powerup":      0.65,
    "obstacle_hit": 0.5,
    "engine":       0.18,   # Engine is background — kept quiet
}


class SoundManager:
    """
    Loads all .wav files at startup and exposes simple play/stop methods.
    If 'enabled' is False (sound turned off in settings), all methods silently do nothing.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled               # Master on/off switch from settings
        self._sounds: dict[str, pygame.mixer.Sound] = {}   # name → Sound object
        self._engine_channel = None          # Holds the channel used for the looping engine sound

        if not enabled:
            return   # Don't bother loading files if sound is disabled

        # Load every sound file listed in SOUND_FILES
        for name, filename in SOUND_FILES.items():
            path = os.path.join(SOUNDS_DIR, filename)
            try:
                snd = pygame.mixer.Sound(path)           # Load .wav into memory
                snd.set_volume(VOLUMES.get(name, 0.5))   # Apply per-sound volume
                self._sounds[name] = snd                 # Store for later use
            except Exception as e:
                # Warn in the console but don't crash — missing audio is not fatal
                print(f"[SoundManager] could not load {path}: {e}")

    def play(self, name: str, loops: int = 0):
        """
        Play a sound effect once (or 'loops' extra times).
        Does nothing if sound is disabled or the file failed to load.
        """
        if not self.enabled:
            return
        snd = self._sounds.get(name)
        if snd:
            try:
                snd.play(loops=loops)   # loops=0 means play once; loops=-1 means infinite loop
            except Exception:
                pass   # Silently ignore playback errors

    def start_engine(self):
        """
        Start the engine sound on an infinite loop (-1).
        Only starts a new loop if the engine is not already playing.
        Called once at the beginning of a gameplay session.
        """
        if not self.enabled:
            return
        try:
            snd = self._sounds.get("engine")
            if snd and (self._engine_channel is None or
                        not self._engine_channel.get_busy()):
                # play(loops=-1) repeats indefinitely; returns the Channel it plays on
                self._engine_channel = snd.play(loops=-1)
        except Exception:
            pass

    def stop_engine(self):
        """
        Stop the engine loop immediately.
        Called when the player crashes (game over).
        """
        if self._engine_channel:
            try:
                self._engine_channel.stop()
            except Exception:
                pass
            self._engine_channel = None   # Reset so start_engine() can restart it later

    def set_engine_pitch(self, speed: int):
        """
        Simulate a higher engine pitch at higher speeds by increasing volume.
        The engine sound file stays the same, but louder = perceived as faster.
        Volume is capped at 0.40 to avoid distortion.
        Formula: vol = 0.12 + speed * 0.015  (e.g. speed 6 → vol 0.21, speed 16 → vol 0.36)
        """
        if not self.enabled:
            return
        snd = self._sounds.get("engine")
        if snd:
            vol = min(0.40, 0.12 + speed * 0.015)
            snd.set_volume(vol) # Adjust the volume of the engine sound to simulate pitch change with speed

    def stop_all(self):
        """
        Stop every sound channel immediately.
        Called when the player quits the game entirely.
        """
        if not self.enabled:
            return
        pygame.mixer.stop()       # Stops all active channels at once
        self._engine_channel = None   # Reset engine channel reference as well  