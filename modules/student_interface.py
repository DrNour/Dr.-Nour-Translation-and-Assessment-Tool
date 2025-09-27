import streamlit as st
import json
from pathlib import Path

EXERCISE_FILE = Path(__file__).parent / "exercises.json"

try:
  # modules/postediting.py
from difflib import SequenceMatcher

def calculate_edit_distance(original, student_translation):
    """Compute a simple edit distance between two strings."""
    if not original or not student_translation:
        return 0

    matcher = SequenceMatcher(None, original, student_translation)
    
    # Opcodes are tuples: (tag, i1, i2, j1, j2)
    distance = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            distance += max(i2 - i1, j2 - j1)
    return distance

def calculate_edit_ratio(original, student_translation):
    """Compute edit ratio: number of edits / length of original."""
    distance = calculate_edit_distance(original, student_translation)
    return distance / max(len(original), 1)  # avoid division by zero


def load_exercises():
    if EXERCISE_FILE.exists():
        with open(EXERCISE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def student_dashboard():
    st.header("Student Dashboard")

    exercises = load_exercises()
    if not exercises:
        st.info("No exercises available. Please wait for instructor to create some.")
        return

    # Show exercises one by one (or allow selection)
    exercise = st.selectbox("Select Exercise", exercises, format_func=lambda x: x["text"][:50]+"..." if len(x["text"])>50 else x["text"])
    original_text = exercise.get("text", "")
    reference_translation = exercise.get("reference", "")

    # Student translation
    student_translation = st.text_area("Your Translation")

    if st.button("Submit Translation"):
        if not student_translation.strip():
            st.warning("Please enter a translation before submitting.")
        else:
            st.success("Translation submitted successfully!")

            if calculate_edit_distance and original_text.strip():
                distance = calculate_edit_distance(original_text, student_translation)
                ratio = calculate_edit_ratio(original_text, student_translation)
                st.write(f"Edit Distance: {distance}")
                st.write(f"Edit Ratio: {ratio:.2f}")
            else:
                st.info("Post-edit metrics unavailable (no original text or module missing).")

