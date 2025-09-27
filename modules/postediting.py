import streamlit as st

def calculate_edit_distance(original, edited):
    # Dummy implementation
    return abs(len(original) - len(edited))

def calculate_edit_ratio(original, edited):
    # Dummy implementation
    return 1.0 if original == edited else 0.5

def highlight_errors(text):
    # Dummy highlighting
    return text.replace("error", "**error**")

class PostEditSession:
    def __init__(self):
        self.keystrokes = 0
        self.time_spent = 0

    def start(self):
        import time
        self._start_time = time.time()

    def end(self):
        import time
        self.time_spent = time.time() - self._start_time
