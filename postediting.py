# modules/postedit_metrics.py
import streamlit as st

def calculate_edit_distance(original, edited):
    # Simple placeholder for edit distance
    return abs(len(original) - len(edited))

def calculate_edit_ratio(original, edited):
    # Simple placeholder for edit ratio
    if len(original) == 0:
        return 0
    return calculate_edit_distance(original, edited) / len(original)

def highlight_errors(original, edited):
    # Dummy function to "highlight" differences
    errors = []
    min_len = min(len(original), len(edited))
    for i in range(min_len):
        if original[i] != edited[i]:
            errors.append((i, original[i], edited[i]))
    return errors

class PostEditSession:
    def __init__(self, original, edited):
        self.original = original
        self.edited = edited
        self.edit_distance = calculate_edit_distance(original, edited)
        self.edit_ratio = calculate_edit_ratio(original, edited)
        self.errors = highlight_errors(original, edited)

    def summary(self):
        return {
            "edit_distance": self.edit_distance,
            "edit_ratio": self.edit_ratio,
            "errors": self.errors
        }
