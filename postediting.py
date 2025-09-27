# postedit_metrics.py
import time
from difflib import SequenceMatcher

def calculate_edit_distance(source: str, target: str) -> int:
    """Compute character-level edit distance."""
    matcher = SequenceMatcher(None, source, target)
    return int((1 - matcher.ratio()) * max(len(source), len(target)))

def calculate_edit_ratio(source: str, target: str) -> float:
    """Return normalized edit distance (0.0-1.0)."""
    return calculate_edit_distance(source, target) / max(len(source), len(target))

def highlight_errors(source: str, target: str) -> list:
    """
    Identify and return error positions (as tuples of source idx, target idx).
    Useful for highlighting.
    """
    matcher = SequenceMatcher(None, source, target)
    errors = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            errors.append((i1, i2, j1, j2, tag))
    return errors

class PostEditSession:
    """Track editing time and keystrokes."""
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.keystrokes = 0

    def start(self):
        self.start_time = time.time()
        self.keystrokes = 0

    def end(self):
        self.end_time = time.time()

    def add_keystrokes(self, n: int):
        self.keystrokes += n

    def get_duration(self):
        if self.start_time and self.end_time:
            return round(self.end_time - self.start_time, 2)
        return 0

    def summary(self):
        return {
            "keystrokes": self.keystrokes,
            "duration_sec": self.get_duration()
        }
