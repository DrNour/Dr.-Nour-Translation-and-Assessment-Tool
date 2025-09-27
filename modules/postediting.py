import streamlit as st

def award_badges(score):
    badges = []
    if score > 90:
        badges.append("🌟 Expert Translator")
    elif score > 70:
        badges.append("🔥 Rising Star")
    else:
        badges.append("🎯 Beginner")
    st.subheader("🏅 Your Badges")
    for badge in badges:
        st.write(badge)
    return badges
# modules/postediting.py

import time

def calculate_edit_distance(src, tgt):
    # Example: simple Levenshtein distance placeholder
    return sum(1 for a, b in zip(src, tgt) if a != b) + abs(len(src) - len(tgt))

def calculate_edit_ratio(src, tgt):
    distance = calculate_edit_distance(src, tgt)
    return distance / max(len(src), 1)

def highlight_errors(src, tgt):
    errors = []
    for i, (s, t) in enumerate(zip(src, tgt)):
        if s != t:
            errors.append((i, s, t))
    return errors

class PostEditSession:
    def __init__(self):
        self.start_time = time.time()
        self.keystrokes = 0

    def add_keystrokes(self, n):
        self.keystrokes += n

    def get_time_spent(self):
        return time.time() - self.start_time
