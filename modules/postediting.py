# modules/postediting.py
from difflib import SequenceMatcher

def calculate_edit_distance(original, student_translation):
    """Compute edit distance between two strings."""
    if not original or not student_translation:
        return 0
    matcher = SequenceMatcher(None, original, student_translation)
    distance = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            distance += max(i2 - i1, j2 - j1)
    return distance

def calculate_edit_ratio(original, student_translation):
    """Compute edit ratio: number of edits / length of original."""
    distance = calculate_edit_distance(original, student_translation)
    return distance / max(len(original), 1)  # avoid division by zero

def highlight_errors(original, student_translation):
    """Return a list of tuples (error_type, original_part, student_part)"""
    matcher = SequenceMatcher(None, original, student_translation)
    errors = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            errors.append((tag, original[i1:i2], student_translation[j1:j2]))
    return errors

class PostEditSession:
    """Simple session to track post-editing metrics."""
    def __init__(self, original, student_translation):
        self.original = original
        self.student_translation = student_translation
        self.distance = calculate_edit_distance(original, student_translation)
        self.ratio = calculate_edit_ratio(original, student_translation)
        self.errors = highlight_errors(original, student_translation)

    def summary(self):
        return {
            "edit_distance": self.distance,
            "edit_ratio": self.ratio,
            "errors": self.errors
        }
