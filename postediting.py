from difflib import SequenceMatcher
import time

class PostEditSession:
    def __init__(self, source, mt_output, student_output):
        self.source = source
        self.mt_output = mt_output
        self.student_output = student_output
        self.start_time = time.time()
        self.end_time = None

    def end(self):
        self.end_time = time.time()

    def editing_time(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

def calculate_edit_distance(mt_output, student_output):
    return sum(1 for a, b in zip(mt_output, student_output) if a != b)

def calculate_edit_ratio(mt_output, student_output):
    matcher = SequenceMatcher(None, mt_output, student_output)
    return 1 - matcher.ratio()

def highlight_errors(source, student_output):
    errors = []
    if not student_output.endswith("."):
        errors.append("Missing final period.")
    return errors
