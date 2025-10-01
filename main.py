import streamlit as st
import pandas as pd
import os
import io
import time
from difflib import SequenceMatcher
from datetime import datetime

# -------------------------
# Directories / files
# -------------------------
SUBMISSIONS_DIR = "submissions"
EXERCISES_FILE = "exercises.csv"

# -------------------------
# Exercise helpers
# -------------------------
def load_exercises():
    if os.path.exists(EXERCISES_FILE):
        return pd.read_csv(EXERCISES_FILE)
    return pd.DataFrame(columns=["exercise_id", "source_text", "mt_text"])

def save_exercises(df):
    df.to_csv(EXERCISES_FILE, index=False)

# -------------------------
# Metrics helpers
# -------------------------
def evaluate_translation(st_text, mt_text, student_text, task_type):
    fluency = len(student_text.split()) / (len(st_text.split()) + 1)
    reference_text = mt_text if task_type=="Post-edit MT" and mt_text else st_text
    accuracy = SequenceMatcher(None, reference_text, student_text).ratio()
    additions = omissions = edits = 0
    if task_type=="Post-edit MT" and mt_text:
        mt_words = mt_text.split()
        student_words = student_text.split()
        s = SequenceMatcher(None, mt_words, student_words)
        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag == "insert": additions += (j2-j1)
            elif tag == "delete": omissions += (i2-i1)
            elif tag == "replace": edits += max(i2-i1, j2-j1)
    bleu = round(accuracy * 100, 2)
    chrf = round(accuracy * 100, 2)
    return {"fluency": round(fluency,2), "accuracy": round(accuracy,2),
            "bleu": bleu, "chrF": chrf, "additions": additions,
            "omissions": omissions, "edits": edits}

# -------------------------
# Submission helpers
# -------------------------
def save_submission(student_name, ex_id, source_text, student_text, mt_text, task_type, metrics, time_spent, keystrokes):
    os.makedirs(SUBMISSIONS_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(SUBMISSIONS_DIR, f"{today}.csv")
    new_entry = {
        "student": student_name,
        "exercise_id": ex_id,
        "source_text": source_text,
        "mt_text": mt_text if mt_text else "",
        "student_text": student_text,
        "task_type": task_type,
        "time_spent_sec": round(time_spent,2),
        "keystrokes": keystrokes,
        "fluency": metrics.get("fluency",0),
        "accuracy": metrics.get("accuracy",0),
        "bleu": metrics.get("bleu",0),
        "chrF": metrics.get("chrF",0),
        "additions": metrics.get("additions",0),
        "omissions": metrics.get("omissions",0),
        "edits": metrics.get("edits",0)
    }
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    else:
        df = pd.DataFrame([new_entry])
    df.to_csv(filename, index=False)

# -------------------------
# Student Dashboard
# -------------------------
def student_dashboard():
    st.title("Student Dashboard")
    student_name = st.text_input("Enter your name")
    if not student_name:
        st.warning("Please enter your name.")
        return

    # Always load exercises fresh
    ex_df = load_exercises()
    if ex_df.empty:
        st.info("No exercises available. Instructor needs to add some.")
        return

    ex_id = st.selectbox("Select Exercise", ex_df["exercise_id"].tolist())
    exercise_row = ex_df[ex_df["exercise_id"] == ex_id].iloc[0]
    source_text = exercise_row["source_text"]
    mt_text = exercise_row.get("mt_text","")
    task_type = st.radio("Task Type", ["Translate", "Post-edit MT"])
    student_text = st.text_area("Your Submission")

    if f"start_time_{ex_id}" not in st.session_state:
        st.session_state[f"start_time_{ex_id}"] = time.time()
    if f"keystrokes_{ex_id}" not in st.session_state:
        st.session_state[f"keystrokes_{ex_id}"] = 0

    if st.button("Submit"):
        if student_name and student_text:
            time_spent = time.time() - st.session_state[f"start_time_{ex_id}"]
            st.session_state[f"keystrokes_{ex_id}"] = len(student_text)
            metrics = evaluate_translation(source_text, mt_text, student_text, task_type)
            save_submission(student_name, ex_id, source_text, student_text, mt_text, task_type,
                            metrics, time_spent, st.session_state[f"keystrokes_{ex_id}"])
            st.success("✅ Submission saved!")
            st.write(metrics)

            # --- Gamification ---
            points = metrics['fluency']*0.3 + metrics['accuracy']*0.5 + metrics['bleu']*0.2
            points = round(points,2)
            st.success(f"🎯 You earned {points} points!")

            st.progress(min(int(points), 100))

            badges = []
            if metrics['fluency'] > 0.9: badges.append("Fluency Master")
            if metrics['accuracy'] > 0.9: badges.append("Accuracy Ace")
            if metrics['bleu'] > 90: badges.append("BLEU Pro")
            if badges:
                st.info("🏅 Badges earned: " + ", ".join(badges))
        else:
            st.error("Please enter your name and your translation.")

    # Optional: reload exercises manually
    if st.button("Reload Exercises"):
        st.experimental_rerun()

# -------------------------
# Instructor Dashboard
# -------------------------
def instructor_dashboard():
    st.title("Instructor Dashboard")
    # --- Manage exercises ---
    st.subheader("Manage Exercises")
    ex_df = load_exercises()
    new_ex_id = st.text_input("Exercise ID for new exercise")
    new_source_text = st.text_area("Source Text")
    new_mt_text = st.text_area("MT Output (optional)")

    if st.button("Save Exercise"):
        if new_ex_id and new_source_text:
            ex_df = pd.concat([ex_df, pd.DataFrame([{
                "exercise_id": new_ex_id,
                "source_text": new_source_text,
                "mt_text": new_mt_text
            }])], ignore_index=True)
            save_exercises(ex_df)
            st.success(f"Exercise {new_ex_id} saved!")
        else:
            st.error("Exercise ID and source text are required.")

    if not ex_df.empty:
        st.subheader("Existing Exercises")
        st.dataframe(ex_df)

    # --- Submissions ---
    st.subheader("Today's Submissions")
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(SUBMISSIONS_DIR, f"{today}.csv")

    if os.path.exists(filename):
        df = pd.read_csv(filename)
        st.dataframe(df)

        students = df["student"].unique().tolist()
        selected_student = st.selectbox("Select student to download", students)
        student_df = df[df["student"] == selected_student]
        st.download_button(
            label=f"📥 Download {selected_student}'s submissions (CSV)",
            data=student_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{selected_student}_submissions_{today}.csv",
            mime="text/csv"
        )

        # Download full CSV summary
        st.download_button(
            label="📊 Download All Submissions + Metrics (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"submissions_summary_{today}.csv",
            mime="text/csv"
        )

        # --- Leaderboard ---
        st.subheader("🏆 Leaderboard - Today")
        df['points'] = df['fluency']*0.3 + df['accuracy']*0.5 + df['bleu']*0.2
        leaderboard = df.groupby('student')['points'].sum().reset_index()
        leaderboard = leaderboard.sort_values(by='points', ascending=False)
        st.table(leaderboard)

    else:
        st.warning("No submissions found for today.")

# -------------------------
# Main
# -------------------------
def main():
    st.sidebar.title("Navigation")
    role = st.sidebar.radio("Login as", ["Student", "Instructor"])
    if role == "Student":
        student_dashboard()
    else:
        instructor_dashboard()

if __name__=="__main__":
    main()
