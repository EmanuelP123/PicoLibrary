"""
Trace.py - Mini-Lab 4: IoT CRM Browser
Author: Emanuel Petrini

Prints every message between objects in the same form as the sequence
diagrams, with the time since start, so the console output can be compared
line by line with the diagrams (and the two loading options can be timed).
"""

import time


def _now_ms():
    """Milliseconds from a free-running clock (MicroPython or desktop Python)."""
    if hasattr(time, "ticks_ms"):
        return time.ticks_ms()
    return int(time.time() * 1000)


def _diff_ms(a, b):
    """a - b in milliseconds, handling MicroPython's wrapping tick counter."""
    if hasattr(time, "ticks_diff"):
        return time.ticks_diff(a, b)
    return a - b


class Trace:
    """Static helper that prints sequence-diagram style messages."""

    _start = _now_ms()

    @staticmethod
    def now():
        """Return the current clock value in ms (used to time operations)."""
        return _now_ms()

    @staticmethod
    def since(start):
        """Return the ms elapsed since a value returned by now()."""
        return _diff_ms(_now_ms(), start)

    @staticmethod
    def reset():
        """Restart the trace clock at 0."""
        Trace._start = _now_ms()

    @staticmethod
    def call(source, target, message):
        """Print a synchronous call arrow: source -> target: message."""
        t = _diff_ms(_now_ms(), Trace._start) / 1000
        print(f"[{t:8.3f}s] {source} -> {target}: {message}")

    @staticmethod
    def reply(source, target, message):
        """Print a return arrow: source <-- target: message."""
        t = _diff_ms(_now_ms(), Trace._start) / 1000
        print(f"[{t:8.3f}s] {source} <-- {target}: {message}")

    @staticmethod
    def note(message):
        """Print a note line (state changes, totals)."""
        t = _diff_ms(_now_ms(), Trace._start) / 1000
        print(f"[{t:8.3f}s] -- {message}")
