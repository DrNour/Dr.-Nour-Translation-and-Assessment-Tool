import streamlit as st
import time
from difflib import SequenceMatcher
from collections import defaultdict
from transformers import pipeline
import pandas as pd

# Initialize translation metrics pipelines
try:
    bleu_scorer = pipeline("translation", model="Helsinki-NLP/opus-mt-en-de")  # Example MT metric
except Exception:
    bleu_scorer = None

# In-memory storage for simplicity
student_scores = defaultdict(list)

# --- Utility functions ---
def compute_edit_distance(original, edited):
    """Calculate a simple edit distance between two texts."""
    return int((1 - SequenceMatcher(None, original, edited).ratio()) * max(len(original), len(edited)))

def compute_score(submission, reference=None):
    """Compute fluency/accuracy metrics. If no reference, only fluency estimation."""
    # Dummy fluency scoring (later can integrate language models)
    fluency_score = min(len(submission.split()) / 50, 1.0) * 100

    if reference:
        edit_distance = compute_edit_distance(reference, submission)
        accuracy_score = max(0, 100 - edit_distance)
    else:
        accuracy_score = None
        edit_distance = None

    return fluency_score, accuracy_score, edit_distance

def categorize_errors(submission, reference=None):
    """Highlight simple error types."""
    if not reference:
        return []
    errors = []
    submission_words = submission.split()
    reference_words = reference.split()
    for i, (s, r) in enumerate(zip(submission_words, reference_words)):
        if s != r:
            errors.append({"position": i, "submitted": s, "expected": r, "type": "mismatch"})
    return errors

# --- Student interface ---
def student_interface():
    st.header("Student Translation & Post-Editing")
    
    mode = st.radio("Mode:", ["Translate from scratch", "Post-edit MT output"])
    submission = st.text_area("Enter your translation here:")
    reference = st.text_area("Reference text (optional):")
    
    start_time = time.time()
    
    if st.button("Submit"):
        time_taken = time.time() - start_time
        fluency, accuracy, edit_distance = compute_score(submission, reference if reference else None)
        errors = categorize_errors(submission, reference if reference else None)
        
        student_scores[st.session_state.get('student_name', 'anonymous')].append({
            "fluency": fluency,
            "accuracy": accuracy,
            "edit_distance": edit_distance,
            "time": time_taken,
            "errors": errors,
            "mode": mode
        })
        
        st.success("Submission recorded!")
        st.write(f"Fluency: {fluency:.2f}%")
        if accuracy is not None:
            st.write(f"Accuracy: {accuracy:.2f}%")
        st.write(f"Editing effort (time): {time_taken:.2f} seconds")
        st.write(f"Edit distance: {edit_distance}")
        st.write("Errors detected:", errors)

# --- Instructor interface ---
def instructor_interface():
    st.header("Instructor Panel")
    
    st.subheader("Add New Exercise")
    exercise_text = st.text_area("Exercise text:")
    if st.button("Add Exercise"):
        # For now, just display a success message
        st.success("Exercise added! (Stored in memory for demo)")
    
    st.subheader("Download Student Submissions")
    all_data = []
    for student, submissions in student_scores.items():
        for i, sub in enumerate(submissions):
            row = sub.copy()
            row["student"] = student
            row["submission_no"] = i + 1
            all_data.append(row)
    
    if all_data:
        df = pd.DataFrame(all_data)
        st.download_button("Download CSV", df.to_csv(index=False), "submissions.csv", "text/csv")
    else:
        st.info("No submissions yet.")

# --- Leaderboard ---
def leaderboard():
    st.header("Leaderboard")
    leaderboard_data = []
    for student, subs in student_scores.items():
        total_score = 0
        count = 0
        for s in subs:
            score = (s["fluency"] or 0) + (s["accuracy"] or 0)
            total_score += score
            count += 1
        if count:
            leaderboard_data.append({"student": student, "avg_score": total_score / count})
    
    if leaderboard_data:
        df = pd.DataFrame(sorted(leaderboard_data, key=lambda x: x["avg_score"], reverse=True))
        st.table(df)
    else:
        st.info("No scores yet.")

# --- Main runner ---
def run_interface():
    st.sidebar.header("Choose Interface")
    page = st.sidebar.selectbox("Interface", ["Student", "Instructor", "Leaderboard"])
    
    if page == "Student":
        student_interface()
    elif page == "Instructor":
        instructor_interface()
    elif page == "Leaderboard":
        leaderboard()
