import streamlit as st
import json
from pathlib import Path

EXERCISE_FILE = Path(__file__).parent / "exercises.json"

try:
    from modules.postediting import calculate_edit_distance, calculate_edit_ratio
except ModuleNotFoundError:
    calculate_edit_distance = calculate_edit_ratio = None

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
