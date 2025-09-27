import streamlit as st
import time
from difflib import SequenceMatcher
import pandas as pd

# ------------------------------
# Session state setup
# ------------------------------
if 'submissions' not in st.session_state:
    st.session_state.submissions = []

if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = {}

if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# ------------------------------
# Helper functions
# ------------------------------
def edit_distance(a, b):
    """Simple Levenshtein-like distance using SequenceMatcher"""
    return int((1 - SequenceMatcher(None, a, b).ratio()) * max(len(a), len(b)))

def categorize_errors(candidate, reference=None, mt_output=None):
    errors = []
    if reference:
        candidate_words = set(candidate.split())
        reference_words = set(reference.split())
        mt_words = set(mt_output.split()) if mt_output else set()
        
        lexical_errors = len(candidate_words - reference_words)
        errors.append(f"Lexical errors: {lexical_errors}")
        
        if mt_output:
            unchanged = len([w for w in candidate.split() if w in mt_words])
            errors.append(f"MT unchanged words: {unchanged}")
        
        if len(candidate.split()) != len(reference.split()):
            errors.append("Possible grammatical errors")
    return errors

def evaluate_translation(candidate, reference=None, mt_output=None):
    """Return evaluation metrics"""
    metrics = {}
    if reference:
        metrics['Length ratio'] = len(candidate.split()) / len(reference.split())
        metrics['Edit distance'] = edit_distance(candidate, reference)
        metrics['Errors'] = categorize_errors(candidate, reference, mt_output)
    return metrics

def add_points(student_name, points):
    if student_name not in st.session_state.leaderboard:
        st.session_state.leaderboard[student_name] = 0
    st.session_state.leaderboard[student_name] += points

# ------------------------------
# Interface selection
# ------------------------------
st.title("Translation Evaluation Tool")
mode = st.radio("Select interface", ["Student", "Instructor"])

# ------------------------------
# Student Interface
# ------------------------------
if mode == "Student":
    student_name = st.text_input("Enter your name:")
    use_mt = st.checkbox("Start from MT output?")
    mt_translation = ""
    reference_translation = st.text_area("Optional reference translation:")

    if use_mt:
        mt_translation = st.text_area("MT Output", value="The quick brown fox jumps over the lazy dog.")

    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    student_translation = st.text_area("Your Translation:", mt_translation or "")

    if st.button("Submit Translation") and student_name:
        elapsed_time = time.time() - st.session_state.start_time
        st.session_state.start_time = None

        edit_dist = edit_distance(mt_translation, student_translation) if use_mt else 0

        # Evaluate translation
        results = evaluate_translation(student_translation, reference_translation or None, mt_translation if use_mt else None)

        # Gamification points
        points = 10
        if use_mt:
            points += 5
        if edit_dist < 10:
            points += 2
        add_points(student_name, points)

        # Save submission
        st.session_state.submissions.append({
            "Student": student_name,
            "Translation": student_translation,
            "MT Output": mt_translation if use_mt else None,
            "Reference": reference_translation,
            "Time(s)": elapsed_time,
            "Edit Distance": edit_dist,
            "Points": points,
            "Metrics": results
        })

        st.success(f"Submission recorded! You earned {points} points.")
        st.json(results)

# ------------------------------
# Instructor Interface
# ------------------------------
if mode == "Instructor":
    st.subheader("Submissions")
    if st.session_state.submissions:
        for i, sub in enumerate(st.session_state.submissions):
            st.write(f"**Submission {i+1} - {sub['Student']}**")
            st.write(f"Translation: {sub['Translation']}")
            st.write(f"MT Output: {sub['MT Output']}")
            st.write(f"Reference: {sub['Reference']}")
            st.write(f"Time spent: {sub['Time(s)']:.2f}s")
            st.write(f"Edit distance: {sub['Edit Distance']}")
            st.write(f"Points: {sub['Points']}")
            st.write("Metrics:", sub['Metrics'])
            st.markdown("---")
        
        if st.button("Download Submissions as CSV"):
            df = pd.DataFrame(st.session_state.submissions)
            df.to_csv("submissions.csv", index=False)
            st.success("CSV ready! Check your working directory.")

    st.subheader("Leaderboard")
    if st.session_state.leaderboard:
        leaderboard_df = pd.DataFrame(
            sorted(st.session_state.leaderboard.items(), key=lambda x: x[1], reverse=True),
            columns=["Student", "Points"]
        )
        st.table(leaderboard_df)
