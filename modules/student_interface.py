import streamlit as st
import json
from pathlib import Path
from difflib import SequenceMatcher

EXERCISE_FILE = Path(__file__).parent / "exercises.json"
SUBMISSION_FILE = Path(__file__).parent / "submissions.json"

# --- Post-edit metrics ---
def calculate_edit_distance(original, student_translation):
    if not original or not student_translation:
        return 0
    matcher = SequenceMatcher(None, original, student_translation)
    distance = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            distance += max(i2 - i1, j2 - j1)
    return distance

def calculate_edit_ratio(original, student_translation):
    distance = calculate_edit_distance(original, student_translation)
    return distance / max(len(original), 1)

# --- Load exercises ---
def load_exercises():
    if EXERCISE_FILE.exists():
        with open(EXERCISE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- Load/save submissions ---
def load_submissions():
    if SUBMISSION_FILE.exists():
        with open(SUBMISSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_submission(exercise_id, student_translation):
    submissions = load_submissions()
    submissions.append({
        "exercise_id": exercise_id,
        "translation": student_translation
    })
    with open(SUBMISSION_FILE, "w", encoding="utf-8") as f:
        json.dump(submissions, f, indent=2, ensure_ascii=False)

# --- Student dashboard ---
def student_dashboard():
    st.header("Student Dashboard")

    exercises = load_exercises()
    if not exercises:
        st.info("No exercises available. Please wait for instructor to create some.")
        return

    # Select exercise
    exercise = st.selectbox(
        "Select Exercise",
        exercises,
        format_func=lambda x: x["text"][:50] + "..." if len(x["text"]) > 50 else x["text"]
    )
    exercise_id = exercise.get("id")
    original_text = exercise.get("text", "")
    reference_translation = exercise.get("reference", "")

    # Student translation input
    student_translation = st.text_area("Your Translation")

    if st.button("Submit Translation"):
        if not student_translation.strip():
            st.warning("Please enter a translation before submitting.")
        else:
            save_submission(exercise_id, student_translation)
            st.success("Translation submitted successfully!")

            # Post-edit metrics
            if original_text.strip():
                distance = calculate_edit_distance(original_text, student_translation)
                ratio = calculate_edit_ratio(original_text, student_translation)
                st.write(f"Edit Distance: {distance}")
                st.write(f"Edit Ratio: {ratio:.2f}")
            else:
                st.info("Post-edit metrics unavailable (no original text).")
