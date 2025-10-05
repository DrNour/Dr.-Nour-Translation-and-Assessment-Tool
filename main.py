import streamlit as st
import json
import os
import time
from difflib import SequenceMatcher, ndiff
from docx import Document
from docx.shared import RGBColor
from io import BytesIO
import pandas as pd
import random
import requests  # for optional Hugging Face API

# ---------------- Storage ----------------
EXERCISES_FILE = "exercises.json"
SUBMISSIONS_FILE = "submissions.json"
LEADERBOARD_FILE = "leaderboard.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------------- Metrics ----------------
def evaluate_translation(student_text, mt_text=None, reference=None, task_type="Translate", source_text=""):
    fluency = len(student_text.split()) / (len(source_text.split()) + 1)
    ref_text = reference if reference else (mt_text if mt_text and task_type == "Post-edit MT" else None)
    additions = deletions = edits = 0

    if task_type == "Post-edit MT" and mt_text:
        mt_words = mt_text.split()
        student_words = student_text.split()
        s = SequenceMatcher(None, mt_words, student_words)
        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag == "insert": additions += j2 - j1
            elif tag == "delete": deletions += i2 - i1
            elif tag == "replace": edits += max(i2 - i1, j2 - j1)

    if ref_text:
        accuracy = SequenceMatcher(None, ref_text, student_text).ratio()
        ref_words = ref_text.split()
        student_words = student_text.split()
        matches = sum(1 for w in student_words if w in ref_words)
        bleu = matches / (len(student_words) + 1)
        ref_chars = list(ref_text.replace(" ", ""))
        student_chars = list(student_text.replace(" ", ""))
        common = sum(1 for c in student_chars if c in ref_chars)
        precision = common / (len(student_chars) + 1)
        recall = common / (len(ref_chars) + 1)
        chrf = 2 * precision * recall / (precision + recall + 1e-6)
    else:
        accuracy = bleu = chrf = None

    return {
        "fluency": round(fluency, 2),
        "accuracy": round(accuracy, 2) if accuracy is not None else None,
        "bleu": round(bleu, 2) if bleu is not None else None,
        "chrF": round(chrf, 2) if chrf is not None else None,
        "additions": additions,
        "deletions": deletions,
        "edits": edits
    }

# ---------------- Track Changes ----------------
def diff_text(baseline, student_text):
    differ = ndiff(baseline.split(), student_text.split())
    result = []
    for w in differ:
        if w.startswith("- "):
            result.append(f"<span style='color:red;text-decoration:line-through'>{w[2:]}</span>")
        elif w.startswith("+ "):
            result.append(f"<span style='color:green;'>{w[2:]}</span>")
        else:
            result.append(w[2:])
    return " ".join(result)

def add_diff_to_doc(doc, baseline, student_text):
    differ = ndiff(baseline.split(), student_text.split())
    p = doc.add_paragraph()
    for w in differ:
        if w.startswith("- "):
            run = p.add_run(w[2:] + " ")
            run.font.strike = True
            run.font.color.rgb = RGBColor(255, 0, 0)
        elif w.startswith("+ "):
            run = p.add_run(w[2:] + " ")
            run.font.color.rgb = RGBColor(0, 128, 0)
        else:
            p.add_run(w[2:] + " ")

# ---------------- Word Export ----------------
def export_student_word(submissions, student_name):
    doc = Document()
    doc.add_heading(f"Student: {student_name}", 0)
    subs = submissions.get(student_name, {})
    for ex_id, sub in subs.items():
        doc.add_heading(f"Exercise {ex_id}", level=1)
        doc.add_paragraph(f"Source Text:\n{sub['source_text']}")
        if sub.get("mt_text"):
            doc.add_paragraph(f"MT Output:\n{sub['mt_text']}")
        if sub["task_type"] == "Post-edit MT":
            doc.add_paragraph("Student Submission (Track Changes):")
            base = sub.get("mt_text", "")
            add_diff_to_doc(doc, base, sub["student_text"])
        else:
            doc.add_paragraph("Student Submission:")
            doc.add_paragraph(sub["student_text"])
        metrics = sub.get("metrics", {})
        doc.add_paragraph(f"Metrics: {metrics}")
        doc.add_paragraph(f"Task Type: {sub.get('task_type', '')}")
        doc.add_paragraph(f"Time Spent: {sub.get('time_spent_sec', 0):.2f} sec")
        doc.add_paragraph(f"Keystrokes: {sub.get('keystrokes', 0)}")
        doc.add_paragraph("---")
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ---------------- Excel Summary Export ----------------
def export_summary_excel(submissions):
    rows = []
    for student, subs in submissions.items():
        for ex_id, sub in subs.items():
            metrics = sub.get("metrics", {})
            rows.append({
                "Student": student,
                "Exercise": ex_id,
                "Task Type": sub.get("task_type", ""),
                "Fluency": metrics.get("fluency"),
                "Accuracy": metrics.get("accuracy"),
                "BLEU": metrics.get("bleu"),
                "chrF": metrics.get("chrF"),
                "Additions": metrics.get("additions"),
                "Deletions": metrics.get("deletions"),
                "Edits": metrics.get("edits"),
                "Time Spent (s)": sub.get("time_spent_sec", 0),
                "Keystrokes": sub.get("keystrokes", 0)
            })
    df = pd.DataFrame(rows)
    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return buf

# ---------------- Gamification ----------------
def update_leaderboard(student_name, points):
    leaderboard = load_json(LEADERBOARD_FILE)
    leaderboard[student_name] = leaderboard.get(student_name, 0) + points
    save_json(LEADERBOARD_FILE, leaderboard)

def show_leaderboard():
    leaderboard = load_json(LEADERBOARD_FILE)
    if leaderboard:
        st.subheader("Leaderboard (Top 5)")
        top5 = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (name, pts) in enumerate(top5, 1):
            st.write(f"{i}. {name}: {pts} points")
    else:
        st.info("No leaderboard data yet.")

# ---------------- Optional Hugging Face Text Generator ----------------
def ai_generate_text(prompt):
    HF_TOKEN = ""  # 🔒 Leave empty unless you want to activate it later.
    if not HF_TOKEN:
        return None  # Safe fallback
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": prompt}
        response = requests.post("https://api-inference.huggingface.co/models/gpt2", headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()[0]["generated_text"]
    except Exception:
        pass
    return None

# ---------------- Instructor ----------------
def instructor_dashboard():
    st.title("Instructor Dashboard")
    password = st.text_input("Enter instructor password", type="password")
    if password != "admin123":
        st.warning("Incorrect password. Access denied.")
        return

    exercises = load_json(EXERCISES_FILE)
    submissions = load_json(SUBMISSIONS_FILE)

    st.subheader("Create / Edit / Delete Exercise")
    ex_ids = ["New"] + list(exercises.keys())
    selected_ex = st.selectbox("Select Exercise", ex_ids)
    st_text = st.text_area("Source Text", height=150)
    mt_text = st.text_area("MT Output (optional)", height=150)
    if selected_ex != "New":
        st_text = exercises[selected_ex]["source_text"]
        mt_text = exercises[selected_ex].get("mt_text", "")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Save Exercise"):
            next_id = str(max([int(k) for k in exercises.keys()] + [0]) + 1).zfill(3) if selected_ex == "New" else selected_ex
            exercises[next_id] = {"source_text": st_text, "mt_text": mt_text if mt_text.strip() else None}
            save_json(EXERCISES_FILE, exercises)
            st.success(f"Exercise saved! ID: {next_id}")
    with col2:
        if selected_ex != "New" and st.button("Delete Exercise"):
            exercises.pop(selected_ex)
            save_json(EXERCISES_FILE, exercises)
            st.success(f"Exercise {selected_ex} deleted!")
    with col3:
        if st.button("Generate AI Exercise"):
            prompt = "Write a short culturally rich text for translation students."
            ai_text = ai_generate_text(prompt)
            new_text = ai_text if ai_text else f"This is AI generated exercise {random.randint(1,1000)}."
            new_mt = f"MT output for exercise {random.randint(1,1000)}."
            next_id = str(max([int(k) for k in exercises.keys()] + [0]) + 1).zfill(3)
            exercises[next_id] = {"source_text": new_text, "mt_text": new_mt}
            save_json(EXERCISES_FILE, exercises)
            st.success(f"Exercise saved as ID {next_id}")

    st.subheader("Download Exercises")
    for ex_id, ex in exercises.items():
        buf = BytesIO()
        doc = Document()
        doc.add_heading(f"Exercise {ex_id}", 0)
        doc.add_paragraph(f"Source Text:\n{ex['source_text']}")
        if ex.get("mt_text"): doc.add_paragraph(f"MT Output:\n{ex['mt_text']}")
        doc.save(buf); buf.seek(0)
        st.download_button(f"Exercise {ex_id} Word", buf, file_name=f"Exercise_{ex_id}.docx")

    st.subheader("Student Submissions")
    if submissions:
        student_choice = st.selectbox("Choose student", ["All"] + list(submissions.keys()))
        if student_choice != "All":
            buf = export_student_word(submissions, student_choice)
            st.download_button(f"Download {student_choice}'s Submissions", buf, file_name=f"{student_choice}_submissions.docx")
        st.subheader("Download Metrics Summary")
        excel_buf = export_summary_excel(submissions)
        st.download_button("Download Excel Summary", excel_buf, file_name="metrics_summary.xlsx")
        show_leaderboard()
    else:
        st.info("No submissions yet.")

# ---------------- Student ----------------
def student_dashboard():
    st.title("Student Dashboard")
    exercises = load_json(EXERCISES_FILE)
    submissions = load_json(SUBMISSIONS_FILE)
    student_name = st.text_input("Enter your name")
    if not student_name:
        return
    if student_name not in submissions:
        submissions[student_name] = {}

    ex_id = st.selectbox("Choose Exercise", list(exercises.keys()))
    if not ex_id:
        return
    ex = exercises[ex_id]
    st.subheader("Source Text")
    st.markdown(f"<div style='font-family:Times New Roman;font-size:12pt;'>{ex['source_text']}</div>", unsafe_allow_html=True)
    task_options = ["Translate"] if not ex.get("mt_text") else ["Translate", "Post-edit MT"]
    task_type = st.radio("Task Type", task_options)
    initial_text = "" if task_type == "Translate" else ex.get("mt_text", "")
    student_text = st.text_area("Type your translation / post-edit here", initial_text, height=300)

    if f"start_time_{ex_id}" not in st.session_state:
        st.session_state[f"start_time_{ex_id}"] = time.time()
    if f"keystrokes_{ex_id}" not in st.session_state:
        st.session_state[f"keystrokes_{ex_id}"] = 0

    if st.button("Submit"):
        time_spent = time.time() - st.session_state[f"start_time_{ex_id}"]
        st.session_state[f"keystrokes_{ex_id}"] = len(student_text)
        metrics = evaluate_translation(student_text, mt_text=ex.get("mt_text"), reference=None, task_type=task_type, source_text=ex["source_text"])
        submissions[student_name][ex_id] = {
            "source_text": ex["source_text"],
            "mt_text": ex.get("mt_text"),
            "student_text": student_text,
            "task_type": task_type,
            "time_spent_sec": round(time_spent, 2),
            "keystrokes": st.session_state[f"keystrokes_{ex_id}"],
            "metrics": metrics
        }
        save_json(SUBMISSIONS_FILE, submissions)
        st.success("Submission saved!")

        # Assign points for gamification
        points = int(metrics['fluency'] * 10 + (metrics['accuracy'] or 0) * 10)
        update_leaderboard(student_name, points)

        st.subheader("Your Metrics")
        st.markdown(f"""
        - **Fluency:** {metrics['fluency']}
        - **Accuracy:** {metrics['accuracy']}
        - **BLEU:** {metrics['bleu']}
        - **chrF:** {metrics['chrF']}
        - **Additions:** {metrics['additions']}
        - **Deletions:** {metrics['deletions']}
        - **Edits:** {metrics['edits']}
        - **Time Spent:** {round(time_spent, 2)} sec
        - **Keystrokes:** {st.session_state[f"keystrokes_{ex_id}"]}
        """)

        if task_type == "Post-edit MT":
            st.subheader("Track Changes")
            base = ex.get("mt_text", "")
            st.markdown(diff_text(base, student_text), unsafe_allow_html=True)

        show_leaderboard()

# ---------------- Main ----------------
def main():
    st.sidebar.title("Navigation")
    role = st.sidebar.radio("Login as", ["Instructor", "Student"])
    if role == "Instructor":
        instructor_dashboard()
    else:
        student_dashboard()

if __name__ == "__main__":
    main()
