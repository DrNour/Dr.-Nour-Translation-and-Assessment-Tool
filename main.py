import streamlit as st
import json
import os
import time
from difflib import SequenceMatcher, ndiff
from docx import Document
from docx.shared import RGBColor
from io import BytesIO
import pandas as pd

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
def evaluate_translation(st_text, student_text, mt_text=None, reference=None, task_type="Translate"):
    fluency = len(student_text.split()) / (len(st_text.split())+1)

    # Determine reference text
    ref_text = reference if reference else (mt_text if mt_text and task_type=="Post-edit MT" else None)

    additions = deletions = edits = 0
    if task_type=="Post-edit MT" and mt_text:
        mt_words = mt_text.split()
        student_words = student_text.split()
        s = SequenceMatcher(None, mt_words, student_words)
        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag=="insert": additions += j2-j1
            elif tag=="delete": deletions += i2-i1
            elif tag=="replace": edits += max(i2-i1,j2-j1)

    if ref_text:
        accuracy = SequenceMatcher(None, ref_text, student_text).ratio()
        ref_words = ref_text.split()
        student_words = student_text.split()
        matches = sum(1 for w in student_words if w in ref_words)
        bleu = matches / (len(student_words)+1)
        ref_chars = list(ref_text.replace(" ",""))
        student_chars = list(student_text.replace(" ",""))
        common = sum(1 for c in student_chars if c in ref_chars)
        precision = common / (len(student_chars)+1)
        recall = common / (len(ref_chars)+1)
        chrf = 2*precision*recall / (precision+recall+1e-6)
    else:
        accuracy=bleu=chrf=None

    return {
        "fluency": round(fluency,2),
        "accuracy": round(accuracy,2) if accuracy is not None else None,
        "bleu": round(bleu,2) if bleu is not None else None,
        "chrF": round(chrf,2) if chrf is not None else None,
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
            result.append(f"~~{w[2:]}~~")
        elif w.startswith("+ "):
            result.append(f"<span style='color:red;'>{w[2:]}</span>")
        else:
            result.append(w[2:])
    return " ".join(result)

def add_diff_to_doc(doc, baseline, student_text):
    differ = ndiff(baseline.split(), student_text.split())
    p = doc.add_paragraph()
    for w in differ:
        if w.startswith("- "):
            run = p.add_run(w[2:]+" ")
            run.font.strike = True
        elif w.startswith("+ "):
            run = p.add_run(w[2:]+" ")
            run.font.color.rgb = RGBColor(255,0,0)
        else:
            p.add_run(w[2:]+" ")

# ---------------- Word Export ----------------
def export_submissions_word(submissions, student_name):
    doc = Document()
    doc.add_heading(f"Student: {student_name}",0)
    subs = submissions.get(student_name,{})
    for ex_id, sub in subs.items():
        doc.add_heading(f"Exercise {ex_id}", level=1)
        doc.add_paragraph(f"Source Text:\n{sub['source_text']}")
        if sub.get("mt_text"): doc.add_paragraph(f"MT Output:\n{sub['mt_text']}")
        doc.add_paragraph("Student Submission with Track Changes:")
        base = sub.get("mt_text","") if sub["task_type"]=="Post-edit MT" else sub["source_text"]
        add_diff_to_doc(doc, base, sub["student_text"])
        metrics = sub.get("metrics",{})
        doc.add_paragraph(f"Metrics: {metrics}")
        doc.add_paragraph(f"Task Type: {sub.get('task_type','')}")
        doc.add_paragraph(f"Time Spent: {sub.get('time_spent_sec',0):.2f} sec")
        doc.add_paragraph(f"Keystrokes: {sub.get('keystrokes',0)}")
        doc.add_paragraph("---")
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ---------------- Instructor ----------------
def instructor_dashboard():
    st.title("Instructor Dashboard")
    exercises = load_json(EXERCISES_FILE)
    submissions = load_json(SUBMISSIONS_FILE)

    # Create/Edit/Delete
    st.subheader("Create / Edit / Delete Exercise")
    ex_ids = ["New"] + list(exercises.keys())
    selected_ex = st.selectbox("Select Exercise", ex_ids)
    st_text = st.text_area("Source Text", height=150)
    mt_text = st.text_area("MT Output (optional)", height=150)
    if selected_ex != "New":
        st_text = exercises[selected_ex]["source_text"]
        mt_text = exercises[selected_ex].get("mt_text","")
    col1,col2 = st.columns(2)
    with col1:
        if st.button("Save Exercise"):
            next_id = str(max([int(k) for k in exercises.keys()]+[0])+1).zfill(3) if selected_ex=="New" else selected_ex
            exercises[next_id] = {"source_text": st_text, "mt_text": mt_text if mt_text.strip() else None}
            save_json(EXERCISES_FILE, exercises)
            st.success(f"Exercise saved! ID: {next_id}")
    with col2:
        if selected_ex != "New" and st.button("Delete Exercise"):
            exercises.pop(selected_ex)
            save_json(EXERCISES_FILE, exercises)
            st.success(f"Exercise {selected_ex} deleted!")

    # Download exercises
    st.subheader("Download Exercises")
    for ex_id, ex in exercises.items():
        buf = BytesIO()
        doc = Document()
        doc.add_heading(f"Exercise {ex_id}",0)
        doc.add_paragraph(f"Source Text:\n{ex['source_text']}")
        if ex.get("mt_text"): doc.add_paragraph(f"MT Output:\n{ex['mt_text']}")
        doc.save(buf); buf.seek(0)
        st.download_button(f"Exercise {ex_id} Word", buf, file_name=f"Exercise_{ex_id}.docx")

    # Submissions
    st.subheader("Student Submissions")
    if submissions:
        student_choice = st.selectbox("Choose student", ["All"] + list(submissions.keys()))
        if student_choice=="All":
            st.info("Download individual student submissions below.")
        else:
            buf = export_submissions_word(submissions, student_choice)
            st.download_button(f"Download {student_choice}'s Submissions", buf, file_name=f"{student_choice}_submissions.docx")
    else: st.info("No submissions yet.")

# ---------------- Student ----------------
def student_dashboard():
    st.title("Student Dashboard")
    exercises = load_json(EXERCISES_FILE)
    submissions = load_json(SUBMISSIONS_FILE)
    student_name = st.text_input("Enter your name")
    if not student_name: return
    if student_name not in submissions: submissions[student_name]={}

    ex_id = st.selectbox("Choose Exercise", list(exercises.keys()))
    if not ex_id: return
    ex = exercises[ex_id]
    st.subheader("Source Text")
    st.markdown(f"<div style='font-family: Times New Roman; font-size:12pt;'>{ex['source_text']}</div>", unsafe_allow_html=True)

    task_options = ["Translate"] if not ex.get("mt_text") else ["Translate","Post-edit MT"]
    task_type = st.radio("Task Type", task_options)
    initial_text = "" if task_type=="Translate" else ex.get("mt_text","")
    student_text = st.text_area("Your Translation/Post-edit", initial_text, height=300)

    use_mt_as_ref = False
    if ex.get("mt_text"):
        use_mt_as_ref = st.checkbox("Use MT as reference for metrics", value=False)

    if f"start_time_{ex_id}" not in st.session_state: st.session_state[f"start_time_{ex_id}"] = time.time()
    if f"keystrokes_{ex_id}" not in st.session_state: st.session_state[f"keystrokes_{ex_id}"] = 0

    if st.button("Submit"):
        time_spent = time.time()-st.session_state[f"start_time_{ex_id}"]
        st.session_state[f"keystrokes_{ex_id}"] = len(student_text)
        reference = ex.get("reference_text") or (ex.get("mt_text") if use_mt_as_ref else None)
        metrics = evaluate_translation(ex["source_text"], student_text, ex.get("mt_text"), reference, task_type)
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
        st.markdown(f"""
        - **Fluency:** {metrics['fluency']}
        - **Accuracy:** {metrics['accuracy']}
        - **BLEU:** {metrics['bleu']}
        - **chrF:** {metrics['chrF']}
        - **Additions:** {metrics['additions']}
        - **Deletions:** {metrics['deletions']}
        - **Edits:** {metrics['edits']}
        - **Time Spent:** {round(time_spent,2)} sec
        - **Keystrokes:** {st.session_state[f"keystrokes_{ex_id}"]}
        """)

        st.subheader("Track Changes")
        base = ex.get("mt_text","") if task_type=="Post-edit MT" else ex["source_text"]
        st.markdown(diff_text(base, student_text), unsafe_allow_html=True)

# ---------------- Main ----------------
def main():
    st.title("Translation and Assessment Tool")
    role = st.radio("Login as", ["Instructor","Student"])
    if role=="Instructor": instructor_dashboard()
    else: student_dashboard()

if __name__=="__main__":
    main()
