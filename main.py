import streamlit as st
import json
import os
import time
from difflib import SequenceMatcher
from docx import Document
from io import BytesIO
import matplotlib.pyplot as plt

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
            if tag == "insert":
                additions += (j2 - j1)
            elif tag == "delete":
                omissions += (i2 - i1)
            elif tag == "replace":
                edits += max(i2 - i1, j2 - j1)
    
    # Placeholder BLEU/chrF calculations
    try:
        bleu_score = round(accuracy*100,2)
        chrf_score = round(accuracy*100,2)
    except:
        bleu_score = chrf_score = 0

    return {
        "fluency": round(fluency,2),
        "accuracy": round(accuracy,2),
        "bleu": bleu_score,
        "chrf": chrf_score,
        "additions": additions,
        "omissions": omissions,
        "edits": edits
    }

# ---------------- Visualization ----------------
def plot_metrics(metrics):
    categories = ["Fluency","Accuracy","BLEU"]
    values = [metrics["fluency"], metrics["accuracy"], metrics["bleu"]/100]
    fig, ax = plt.subplots(figsize=(4,4))
    ax.barh(categories, values, color=["skyblue","orange","green"])
    ax.set_xlim(0,1)
    for i,v in enumerate(values):
        ax.text(v+0.02,i,f"{v:.2f}")
    st.pyplot(fig)

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
            existing_ids = [int(k) for k in exercises.keys() if k.isdigit()] if exercises else []
            next_id = str(max(existing_ids)+1 if existing_ids else 1).zfill(3)
            exercises[next_id] = {"source_text": st_text, "mt_text": mt_text if mt_text.strip() else None}
            save_json(EXERCISES_FILE, exercises)
            st.success(f"Exercise saved! ID: {next_id}")

    st.subheader("Download Exercises")
    for ex_id, ex in exercises.items():
        if st.button(f"Download Exercise {ex_id}"):
            buf = export_exercise_word(ex_id, ex)
            st.download_button(f"Exercise {ex_id} Word", buf, file_name=f"Exercise_{ex_id}.docx")

    st.subheader("Class Analytics")
    if submissions:
        for ex_id in exercises.keys():
            st.markdown(f"**Exercise {ex_id} Summary**")
            metrics_list = [sub["metrics"] for student, subs in submissions.items() if ex_id in subs for sub in [subs[ex_id]]]
            if metrics_list:
                avg_metrics = {k:round(sum(d[k] for d in metrics_list)/len(metrics_list),2) for k in metrics_list[0].keys()}
                st.write(avg_metrics)
                plot_metrics(avg_metrics)
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
    st.markdown(f"<div style='font-family: Times New Roman; font-size:12pt;'>{ex['source_text']}</div>", unsafe_allow_html=True)

    task_options = ["Translate"] if not ex.get("mt_text") else ["Translate", "Post-edit MT"]
    task_type = st.radio("Task Type", task_options)

    initial_text = "" if task_type=="Translate" else ex.get("mt_text","")
    st.subheader("Your Work")
    student_text = st.text_area("Type your translation / post-edit here", initial_text, height=400)

    # Timer & keystrokes per exercise
    if f"start_time_{ex_id}" not in st.session_state:
        st.session_state[f"start_time_{ex_id}"] = time.time()
    if f"keystrokes_{ex_id}" not in st.session_state:
        st.session_state[f"keystrokes_{ex_id}"] = 0

    if st.button("Submit"):
        time_spent = time.time() - st.session_state[f"start_time_{ex_id}"]
        st.session_state[f"keystrokes_{ex_id}"] = len(student_text)
        metrics = evaluate_translation(ex["source_text"], ex.get("mt_text"), student_text, task_type)
        submissions[student_name][ex_id] = {
            "source_text": ex["source_text"],
            "mt_text": ex.get("mt_text"),
            "student_text": student_text,
            "task_type": task_type,
            "time_spent_sec": round(time_spent,2),
            "keystrokes": st.session_state[f"keystrokes_{ex_id}"],
            "metrics": metrics
        }
        save_json(SUBMISSIONS_FILE, submissions)
        st.success("Submission saved!")

        st.subheader("Your Metrics")
        st.write(metrics)
        plot_metrics(metrics)

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
