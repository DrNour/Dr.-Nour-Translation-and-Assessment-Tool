# modules/postediting.py
from difflib import SequenceMatcher
import streamlit as st
import time

class PostEditSession:
    def __init__(self):
        self.start_time = time.time()
        self.keystrokes = 0

    def record_keystrokes(self, text):
        self.keystrokes = len(text)

    def end_session(self):
        return time.time() - self.start_time  # time spent in seconds

def calculate_edit_distance(original, student_translation):
    if not original or not student_translation:
        return 0
    matcher = SequenceMatcher(None, original, student_translation)
    distance = sum(max(i2-i1, j2-j1) for tag,i1,i2,j1,j2 in matcher.get_opcodes() if tag != 'equal')
    return distance

def calculate_edit_ratio(original, student_translation):
    distance = calculate_edit_distance(original, student_translation)
    return distance / max(len(original), 1)
