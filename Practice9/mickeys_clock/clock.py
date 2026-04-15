"""
clock.py — Time logic for Mickey's Clock
"""
import datetime


def get_current_time():
    """Return (hours, minutes, seconds) from system clock."""
    now = datetime.datetime.now()
    return now.hour, now.minute, now.second


def get_second_angle(seconds: int) -> float:
    """
    Angle for the SECONDS hand.
    0 sec = 0°  (12 o'clock, pointing UP)
    Each second = 6° clockwise.
    Returns degrees clockwise from 12 o'clock.
    """
    return (seconds / 60.0) * 360.0


def format_time(hours: int, minutes: int, seconds: int) -> str:
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"