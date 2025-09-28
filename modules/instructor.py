# modules/instructor.py
import streamlit as st
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

EXERCISE_FILE = Path(__file__).parent / "exercises.json"
SUBMISSION_FILE = Path(__file__).parent / "submissions.json"

def load_exercises():
    if EXERCISE_FILE.exists():
        with open(EXERCISE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_exercises(exercises):
    with open(EXERCISE_FILE, "w", encoding="utf-8") as f:
        json.dump(exercises, f, indent=4, ensure_ascii=False)

def load_submissions():
    if SUBMISSION_FILE.exists():
        with open(SUBMISSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_submission(submission):
    submissions = load_submissions()
    submissions.append(submission)
    with open(SUBMISSION_FILE, "w", encoding="utf-8") as f:
        json.dump(submissions, f, indent=4, ensure_ascii=False)

def instructor_dashboard():
    st.header("Instructor Dashboard")

    # --- Create Exercise ---
    st.subheader("Create New Exercise")
    text = st.text_area("Original Text")
    reference = st.text_area("Reference Translation (Optional)")

    if st.button("Create Exercise"):
        if not text.strip():
            st.warning("Please enter text for the exercise.")
        else:
            exercises = load_exercises()
            exercises.append({
                "id": len(exercises) + 1,
                "text": text.strip(),
                "reference": reference.strip()
            })
            save_exercises(exercises)
            st.success("Exercise created successfully!")

    # --- View Submissions ---
    st.subheader("Student Submissions")
    submissions = load_submissions()
    if submissions:
        df = pd.DataFrame(submissions)
        st.dataframe(df)

        # Download as CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Submissions as CSV",
            data=csv,
            file_name=f"submissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No submissions yet.")
