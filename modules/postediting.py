# modules/postediting.py
import time
from difflib import SequenceMatcher

class PostEditSession:
    def __init__(self, original_text):
        self.original_text = original_text
        self.start_time = time.time()
        self.end_time = None

    def finish(self):
        self.end_time = time.time()
        return self.time_spent()

    def time_spent(self):
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

def calculate_edit_distance(original, student_translation):
    if not original or not student_translation:
        return 0
    matcher = SequenceMatcher(None, original, student_translation)
    distance = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in matcher.get_opcodes() if tag != 'equal')
    return distance

def calculate_edit_ratio(original, student_translation):
    distance = calculate_edit_distance(original, student_translation)
    return distance / max(len(original), 1)
