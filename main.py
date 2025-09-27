try:
    from postediting import run_feature as run_postediting
except Exception:
    run_postediting = None

try:
    from instructor import run_feature as run_instructor
except Exception:
    run_instructor = None

try:
    from student_interface import run_feature as run_student
except Exception:
    run_student = None

import streamlit as st
import pandas as pd
import sacrebleu
from bert_score import score
import os

# File to store exercises and submissions
EXERCISES_FILE = "exercises.csv"
SUBMISSIONS_FILE = "submissions.csv"

# ---------- Helper Functions ----------

def load_exercises():
    if os.path.exists(EXERCISES_FILE):
        return pd.read_csv(EXERCISES_FILE)
    return pd.DataFrame(columns=["id", "source_text", "reference_text"])

def save_exercises(df):
    df.to_csv(EXERCISES_FILE, index=False)

def load_submissions():
    if os.path.exists(SUBMISSIONS_FILE):
        return pd.read_csv(SUBMISSIONS_FILE)
    return pd.DataFrame(columns=["exercise_id", "student_name", "submission", "BLEU", "TER", "BERTScore", "points"])

def save_submissions(df):
    df.to_csv(SUBMISSIONS_FILE, index=False)

def evaluate_translation(submission, reference):
    # BLEU
    bleu = sacrebleu.corpus_bleu([submission], [[reference]]).score if reference else None
    # TER
    ter = sacrebleu.corpus_ter([submission], [[reference]]).score if reference else None
    # BERTScore
    if reference:
        P, R, F1 = score([submission], [reference], lang="en", verbose=False)
        bert = F1.mean().item()
    else:
        bert = None
    return bleu, ter, bert

# ---------- App Layout ----------
st.title("Translation Training App")

mode = st.sidebar.radio("Choose Mode", ["Instructor", "Student"])

# ---------- Instructor Interface ----------
if mode == "Instructor":
    st.header("Instructor Dashboard")

    exercises = load_exercises()

    # Add exercise
    st.subheader("Create New Exercise")
    source_text = st.text_area("Enter Source Text (ST)")
    reference_text = st.text_area("Enter Reference Translation (optional)")
    if st.button("Add Exercise"):
        new_id = len(exercises) + 1
        new_ex = pd.DataFrame([{"id": new_id, "source_text": source_text, "reference_text": reference_text}])
        exercises = pd.concat([exercises, new_ex], ignore_index=True)
        save_exercises(exercises)
        st.success("Exercise added!")

    # Show exercises
    st.subheader("Current Exercises")
    st.dataframe(exercises)

    # Download submissions
    st.subheader("Download Submissions")
    submissions = load_submissions()
    if not submissions.empty:
        st.download_button("Download CSV", submissions.to_csv(index=False), "submissions.csv")
    else:
        st.info("No submissions yet.")

# ---------- Student Interface ----------
else:
    st.header("Student Dashboard")

    exercises = load_exercises()
    submissions = load_submissions()

    if exercises.empty:
        st.warning("No exercises available yet. Please check back later.")
    else:
        # Select exercise
        ex_id = st.selectbox("Choose Exercise", exercises["id"])
        ex_row = exercises[exercises["id"] == ex_id].iloc[0]
        st.write("**Source Text (ST):**")
        st.info(ex_row["source_text"])

        # Student details
        student_name = st.text_input("Enter your name")
        submission = st.text_area("Enter your translation here")

        if st.button("Submit Translation"):
            if student_name and submission:
                bleu, ter, bert = evaluate_translation(submission, ex_row["reference_text"])
                points = 0
                if bleu: points += round(bleu / 10)
                if bert: points += round(bert * 10)

                new_sub = pd.DataFrame([{
                    "exercise_id": ex_id,
                    "student_name": student_name,
                    "submission": submission,
                    "BLEU": bleu,
                    "TER": ter,
                    "BERTScore": bert,
                    "points": points
                }])

                submissions = pd.concat([submissions, new_sub], ignore_index=True)
                save_submissions(submissions)

                st.success("Submission saved and evaluated!")
                st.metric("BLEU", f"{bleu:.2f}" if bleu else "N/A")
                st.metric("TER", f"{ter:.2f}" if ter else "N/A")
                st.metric("BERTScore", f"{bert:.2f}" if bert else "N/A")
                st.metric("Gamification Points", points)
            else:
                st.error("Please enter your name and translation before submitting.")

    # Leaderboard
    st.subheader("Leaderboard")
    if not submissions.empty:
        leaderboard = submissions.groupby("student_name")["points"].sum().reset_index().sort_values("points", ascending=False)
        st.table(leaderboard)
    else:
        st.info("No leaderboard yet.")

