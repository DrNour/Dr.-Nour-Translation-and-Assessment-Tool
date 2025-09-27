import streamlit as st
import json
from pathlib import Path

EXERCISE_FILE = Path(__file__).parent / "exercises.json"

def load_exercises():
    if EXERCISE_FILE.exists():
        with open(EXERCISE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_exercise(exercise):
    exercises = load_exercises()
    exercises.append(exercise)
    with open(EXERCISE_FILE, "w", encoding="utf-8") as f:
        json.dump(exercises, f, ensure_ascii=False, indent=2)

def instructor_dashboard():
    st.header("Instructor Dashboard")
    
    exercise_text = st.text_area("Exercise Text")
    reference_translation = st.text_area("Reference Translation (optional)")
    
    if st.button("Create Exercise"):
        if not exercise_text.strip():
            st.warning("Exercise text cannot be empty")
        else:
            save_exercise({
                "text": exercise_text,
                "reference": reference_translation
            })
            st.success("Exercise saved successfully!")
