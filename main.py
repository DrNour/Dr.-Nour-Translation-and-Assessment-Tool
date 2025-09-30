import streamlit as st
import json
import os
import time
from difflib import SequenceMatcher
from docx import Document
from io import BytesIO
import uuid

# ---------------- Storage ----------------
EXERCISES_FILE = "exercises.json"
SUBMISSIONS_FILE = "submissions.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------------- Metrics ----------------
def evaluate_translation(st_text, mt_text, student_text):
    fluency = len(student_text.split()) / (len(st_text.split()) + 1)
    accuracy = SequenceMatcher(None, mt_text if mt_text else "", student_text).ratio()
    additions = max(0, len(student_text.split()) - len((mt_text or "").split()))
    omissions = max(0, len((mt_text or "").split()) - len(student_text.split()))
    edits = sum(1 for a, b in zip((mt_text or "").split(), student_text.split()) if a != b)
    return {
        "fluency": round(fluency,2),
        "accuracy": round(accuracy,2),
        "additions": additions,
        "omissions": omissions,
        "edits": edits
    }

# ---------------- Word Export ----------------
def export_submissions_word(submissions, filename="submissions.docx"):
    doc = Document()
    doc.add_heading("Student Submissions", 0)
    for student, subs in submissions.items():
        doc.add_heading(f"Student: {student}", level=1)
        for ex_id, sub in subs.items():
            doc.add_heading(f"Exercise {ex_id}", level=2)
            doc.add_paragraph(f"Source Text:\n{sub['source_text']}")
            if sub.get("mt_text"):
                doc.add_paragraph(f"MT Output:\n{sub['mt_text']}")
            doc.add_paragraph(f"Student Submission:\n{sub['student_text']}")
            metrics = sub.get("metrics", {})
            doc.add_paragraph(f"Metrics: {metrics}")
            doc.add_paragraph(f"Task Type: {sub.get('task_type','')}")
            doc.add_paragraph(f"Time Spent: {sub.get('time_spent_sec',0):.2f} sec")
            doc.add_paragraph(f"Keystrokes: {sub.get('keystrokes',0)}")
            doc.add_paragraph("---")
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def export_exercise_word(ex_id, exercise):
    doc = Document()
    doc.add_heading(f"Exercise {ex_id}", 0)
    doc.add_paragraph(f"Source Text:\n{exercise['source_text']}")
    if exercise.get("mt_text"):
        doc.add_paragraph(f"MT Output:\n{exercise['mt_text']}")
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ---------------- Instructor ----------------
def instructor_dashboard():
    st.title("Instructor Dashboard")

    exercises = load_json(EXERCISES_FILE)
    submissions = load_json(SUBMISSIONS_FILE)

    st.subheader("Create New Exercise")
    st_text = st.text_area("Source Text", height=200)
    mt_text = st.text_area("Machine Translation Output (optional)", height=200)

    if st.button("Save Exercise"):
        if st_text.strip() == "":
            st.error("Source text is required.")
        else:
            ex_id = str(uuid.uuid4())
            exercises[ex_id] = {"source_text": st_text, "mt_text": mt_text if mt_text.strip() else None}
            save_json(EXERCISES_FILE, exercises)
            st.success(f"Exercise saved! ID: {ex_id}")

    st.subheader("Download Exercises")
    for ex_id, ex in exercises.items():
        if st.button(f"Download Exercise {ex_id}"):
            buf = export_exercise_word(ex_id, ex)
            st.download_button(f"Exercise {ex_id} Word", buf, file_name=f"Exercise_{ex_id}.docx")

    st.subheader("All Submissions")
    if submissions:
        student_choice = st.selectbox("Choose student", ["All"] + list(submissions.keys()))
        if st.button("Download Word for Selected Student"):
            if student_choice == "All":
                buf = export_submissions_word(submissions)
                st.download_button("Download All Submissions", buf, file_name="all_submissions.docx")
            else:
                buf = export_submissions_word({student_choice: submissions[student_choice]})
                st.download_button(f"Download {student_choice}'s Submissions", buf, file_name=f"{student_choice}_submissions.docx")
    else:
        st.info("No submissions yet.")

# ---------------- Student ----------------
def student_dashboard():
    st.title("Student Dashboard")
    exercises = load_json(EXERCISES_FILE)
    submissions = load_json(SUBMISSIONS_FILE)

    student_name = st.text_input("Enter your name")
    if not student_name:
        st.warning("Please enter your name.")
        return
    if student_name not in submissions:
        submissions[student_name] = {}

    ex_id = st.selectbox("Choose Exercise", list(exercises.keys()))
    if not ex_id:
        st.info("No exercises available yet.")
        return

    ex = exercises[ex_id]
    st.subheader("Source Text")
    st.text_area("ST", ex["source_text"], height=200, disabled=True)

    task_options = ["Translate"] if not ex.get("mt_text") else ["Translate", "Post-edit MT"]
    task_type = st.radio("Task Type", task_options)

    initial_text = "" if task_type=="Translate" else ex.get("mt_text","")
    st.subheader("Your Work")
    student_text = st.text_area("Type your translation / post-edit here", initial_text, height=300)

    if "start_time" not in st.session_state:
        st.session_state["start_time"] = time.time()
    if "keystrokes" not in st.session_state:
        st.session_state["keystrokes"] = 0

    if st.button("Submit"):
        time_spent = time.time() - st.session_state["start_time"]
        metrics = evaluate_translation(ex["source_text"], ex.get("mt_text"), student_text)
        submissions[student_name][ex_id] = {
            "source_text": ex["source_text"],
            "mt_text": ex.get("mt_text"),
            "student_text": student_text,
            "task_type": task_type,
            "time_spent_sec": round(time_spent,2),
            "keystrokes": st.session_state["keystrokes"],
            "metrics": metrics
        }
        save_json(SUBMISSIONS_FILE, submissions)
        st.success("Submission saved!")
        st.json(metrics)

# ---------------- Main ----------------
def main():
    st.sidebar.title("Navigation")
    role = st.sidebar.radio("Login as", ["Instructor", "Student"])
    if role == "Instructor":
        instructor_dashboard()
    else:
        student_dashboard()

if __name__=="__main__":
    main()
