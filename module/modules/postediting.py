import difflib
import time

class PostEditSession:
    def __init__(self):
        self.start_time = time.time()
        self.keystrokes = 0

    def add_keystrokes(self, n):
        self.keystrokes += n

    def elapsed_time(self):
        return time.time() - self.start_time

def calculate_edit_distance(source, target):
    return sum(1 for i in difflib.ndiff(source, target) if i[0] in ('+', '-'))

def calculate_edit_ratio(source, target):
    dist = calculate_edit_distance(source, target)
    return dist / max(len(source), 1)

def highlight_errors(source, target):
    diff = list(difflib.ndiff(source.split(), target.split()))
    return [w for w in diff if w.startswith('-') or w.startswith('+')]

