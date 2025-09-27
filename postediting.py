# postedit_metrics.py
import time

def calculate_edit_distance(src, tgt):
    # Dummy placeholder
    return abs(len(src) - len(tgt))

def calculate_edit_ratio(src, tgt):
    # Dummy placeholder
    if len(src) == 0:
        return 0.0
    return calculate_edit_distance(src, tgt) / len(src)

def highlight_errors(src, tgt):
    # Dummy: highlight differences
    errors = []
    for i, (s_char, t_char) in enumerate(zip(src, tgt)):
        if s_char != t_char:
            errors.append((i, s_char, t_char))
    return errors

class PostEditSession:
    def __init__(self):
        self.start_time = time.time()
        self.keystrokes = 0

    def add_keystrokes(self, count):
        self.keystrokes += count

    def time_spent(self):
        return time.time() - self.start_time
