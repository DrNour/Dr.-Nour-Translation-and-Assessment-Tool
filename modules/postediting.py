import time
from difflib import SequenceMatcher

# --- PostEditSession for time & keystrokes tracking ---
class PostEditSession:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.keystrokes = 0

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()

    def add_keystrokes(self, count):
        self.keystrokes += count

    def time_spent(self):
        if self.start_time and self.end_time:
            return round(self.end_time - self.start_time, 2)
        return 0

# --- Edit Metrics ---
def calculate_edit_distance(original, edited):
    matcher = SequenceMatcher(None, original, edited)
    return int(sum(n for i, j, n in matcher.get_opcodes() if i != j))

def calculate_edit_ratio(original, edited):
    distance = calculate_edit_distance(original, edited)
    max_len = max(len(original), len(edited))
    if max_len == 0:
        return 0
    return round(distance / max_len, 2)

def highlight_errors(original, edited):
    matcher = SequenceMatcher(None, original, edited)
    highlights = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            highlights.append({'type': tag, 'original': original[i1:i2], 'edited': edited[j1:j2]})
    return highlights
