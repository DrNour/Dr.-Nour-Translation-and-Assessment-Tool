import streamlit as st
import json
import os
from evaluation import evaluate_translation

EXERCISE_FILE = "data/exercises.json"
SUBMISSION_FILE = "data/submissions.json"
os.makedirs("data", exist_ok=True)

def load_exercises():
    if os.path.exists(EXERCISE_FILE):
        with open(EXERCISE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_submission(submission):
    submissions = []
    if os.path.exists(SUBMISSION_FILE):
        with open(SUBMISSION_FILE, "r", encoding="utf-8") as f:
            submissions = json.load(f)
    submissions.append(submission)
    with open(SUBMISSION_FILE, "w", encoding="utf-8") as f:
        json.dump(submissions, f, ensure_ascii=False, indent=2)

def student_dashboard():
    st.header("Student Dashboard")

    exercises = load_exercises()
    if not exercises:
        st.info("No exercises available yet. Please check back later.")
        return

    # Select exercise
    titles = [ex["title"] for ex in exercises]
    choice = st.selectbox("Choose an Exercise:", titles)

    selected = next((ex for ex in exercises if ex["title"] == choice), None)

    if selected:
        st.subheader("Source Text")
        st.write(selected["source_text"])

        translation = st.text_area("Your Translation")

        if st.button("Submit Translation"):
            if translation.strip():
                scores = {}
                if selected["reference"].strip():
                    scores = evaluate_translation(translation, selected["reference"])

                submission = {
                    "exercise": selected["title"],
                    "student_translation": translation,
                    "scores": scores
                }
                save_submission(submission)

                st.success("Submission saved successfully!")
                if scores:
                    st.subheader("Evaluation Results")
                    st.json(scores)
            else:
                st.error("Please enter your translation before submitting.")
