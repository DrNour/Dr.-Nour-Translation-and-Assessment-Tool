import streamlit as st
import json
import os
import time
from difflib import SequenceMatcher
from docx import Document
from io import BytesIO

# ----------------- Storage Helpers -----------------
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

# ----------------- Metrics -----------------
def evaluate_translation(st_text, mt_text, student_text):
    """Simple evaluation of translation with edit metrics."""
    fluency = len(student_text.split()) / (len(st_text.split()) + 1)
    accuracy = SequenceMatcher(None, mt_text, student_text).ratio()

    additions = max(0, len(student_text.split()) - len(mt_text.split()))
    omissions = max(0, len(mt_text.split()) - len(student_text.split()))

    edits = sum(1 for a, b in zip(mt_text.split(), student_text.split()) if a != b)

    return {
        "fluency": round(fluency, 2),
        "accuracy": round(accuracy, 2),
        "additions": additions,
        "omissions": omissions,
        "edits": edits,
    }

# ----------------- Word Export -----------------
def export_submissions_word(submissions, filename="submissions.docx"):
    doc = Document()
    doc.add_heading("Student Submissions", 0)

    for student, subs in submissions.items():
        doc.add_heading(f"Student: {student}", level=1)
        for ex_id, sub in subs.items():
            doc.add_heading(f"Exercise {ex_id}", level=2)
            doc.add_paragraph(f"Source Text:\n{sub['source_text']}")
            doc.add_paragraph(f"MT Output:\n{sub['mt_text']}")
            doc.add_paragraph(f"Student Translation:\n{sub['student_text']}")

            metrics = sub.get("metrics", {})
            doc.add_paragraph(f"Fluency: {metrics.get('fluency', 0)}")
            doc.add_paragraph(f"Accuracy: {metrics.get('accuracy', 0)}")
            doc.add_paragraph(f"Additions: {metrics.get('additions', 0)}")
            doc.add_paragraph(f"Omissions: {metrics.get('omissions', 0)}")
            doc.add_paragraph(f"Edits: {metrics.get('edits', 0)}")
            doc.add_paragraph(f"Time Spent: {sub.get('time_spent_sec', 0):.2f} sec")
            doc.add_paragraph(f"Keystrokes: {sub.get('keystrokes', 0)}")
            doc.add_paragraph("---")

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ----------------- Instructor Dashboard -----------------
def instructor_dashboard():
    st.title("Instructor Dashboard")

    exercises = load_json(EXERCISES_FILE)
    submissions = load_json(SUBMISSIONS_FILE)

    st.subheader("Create New Exercise")
    ex_id = str(len(exercises) + 1)
    st_text = st.text_area("Source Text", height=200)
    mt_text = st.text_area("Machine Translation Output", height=200)

    if st.button("Save Exercise"):
        if st_text.strip() and mt_text.strip():
            exercises[ex_id] = {"source_text": st_text, "mt_text": mt_text}
            save_json(EXERCISES_FILE, exercises)
            st.success(f"Exercise {ex_id} saved!")

    st.subheader("All Submissions")
    if submissions:
        student_choice = st.selectbox("Choose student", list(submissions.keys()))
        if student_choice:
            st.write(submissions[student_choice])

        # Download per student
        if st.button("Download This Student's Submissions"):
            buf = export_submissions_word({student_choice: submissions[student_choice]})
            st.download_button("Download Word", buf, file_name=f"{student_choice}_submissions.docx")

        # Download all
        if st.button("Download All Submissions"):
            buf = export_submissions_word(submissions)
            st.download_button("Download Word", buf, file_name="all_submissions.docx")
    else:
        st.info("No submissions yet.")

# ----------------- Student Dashboard -----------------
def student_dashboard():
    st.title("Student Dashboard")

    exercises = load_json(EXERCISES_FILE)
    submissions = load_json(SUBMISSIONS_FILE)

    student_name = st.text_input("Enter your name:")
    if not student_name:
        st.warning("Please enter your name to continue.")
        return

    if student_name not in submissions:
        submissions[student_name] = {}

    ex_id = st.selectbox("Choose Exercise", list(exercises.keys()))
    if not ex_id:
        st.info("No exercises available yet.")
        return

    st_text = exercises[ex_id]["source_text"]
    mt_text = exercises[ex_id]["mt_text"]

    st.subheader("Source Text")
    st.text_area("ST", st_text, height=200, disabled=True)

    st.subheader("Machine Translation Output")
    st.text_area("MT", mt_text, height=200, disabled=True)

    st.subheader("Your Translation / Post-Editing")
    if "start_time" not in st.session_state:
        st.session_state["start_time"] = time.time()
    if "keystrokes" not in st.session_state:
        st.session_state["keystrokes"] = 0

    student_text = st.text_area("Type your translation here:", height=300,
                                key="translation_input", on_change=lambda: increment_keystrokes())

    if st.button("Submit Translation"):
        time_spent = time.time() - st.session_state["start_time"]
        metrics = evaluate_translation(st_text, mt_text, student_text)

        submissions[student_name][ex_id] = {
            "source_text": st_text,
            "mt_text": mt_text,
            "student_text": student_text,
            "time_spent_sec": round(time_spent, 2),
            "keystrokes": st.session_state["keystrokes"],
            "metrics": metrics,
        }

        save_json(SUBMISSIONS_FILE, submissions)
        st.success("✅ Submission saved!")

        st.json(metrics)

def increment_keystrokes():
    st.session_state["keystrokes"] += 1

# ----------------- Main -----------------
def main():
    st.sidebar.title("Navigation")
    role = st.sidebar.radio("Login as:", ["Student", "Instructor"])

    if role == "Student":
        student_dashboard()
    else:
        instructor_dashboard()

if __name__ == "__main__":
    main()
