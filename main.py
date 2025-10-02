import streamlit as st
import json
import os
import time
from difflib import SequenceMatcher, ndiff
from docx import Document
from io import BytesIO

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
def evaluate_translation(baseline_text, student_text, reference=None):
    # Fluency reference-free
    fluency = len(student_text.split()) / (len(baseline_text.split()) + 1)

    # Track additions, deletions, edits
    additions = deletions = edits = 0
    sm = SequenceMatcher(None, baseline_text.split(), student_text.split())
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "insert":
            additions += j2 - j1
        elif tag == "delete":
            deletions += i2 - i1
        elif tag == "replace":
            edits += max(i2 - i1, j2 - j1)

    # Compute accuracy, BLEU, chrF only if reference exists
    if reference:
        accuracy = SequenceMatcher(None, reference, student_text).ratio()
        ref_words = reference.split()
        student_words = student_text.split()
        matches = sum(1 for w in student_words if w in ref_words)
        bleu = matches / (len(student_words)+1)

        ref_chars = list(reference.replace(" ", ""))
        student_chars = list(student_text.replace(" ", ""))
        common = sum(1 for c in student_chars if c in ref_chars)
        precision = common / (len(student_chars)+1)
        recall = common / (len(ref_chars)+1)
        chrf = 2*precision*recall / (precision+recall+1e-6)
    else:
        accuracy = bleu = chrf = None

    return {
        "fluency": round(fluency,2),
        "accuracy": round(accuracy,2) if accuracy is not None else None,
        "bleu": round(bleu,2) if bleu is not None else None,
        "chrF": round(chrf,2) if chrf is not None else None,
        "additions": additions,
        "deletions": deletions,
        "edits": edits
    }

# ---------------- Track changes ----------------
def diff_text(baseline, student_text):
    differ = ndiff(baseline.split(), student_text.split())
    result = []
    for w in differ:
        if w.startswith("- "):
            # deletions strikethrough
            result.append(f"~~{w[2:]}~~")
        elif w.startswith("+ "):
            # insertions in red
            result.append(f"<span style='color:red;'>{w[2:]}</span>")
        else:
            result.append(w[2:])
    return " ".join(result)

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

    st.subheader("Create / Edit Exercise")
    st_text = st.text_area("Source Text", height=200)
    mt_text = st.text_area("Machine Translation Output (optional)", height=200)

    selected_ex = st.selectbox("Select Exercise to Edit", ["New"] + list(exercises.keys()))
    if selected_ex != "New":
        st_text = exercises[selected_ex]["source_text"]
        mt_text = exercises[selected_ex].get("mt_text","")

    if st.button("Save Exercise"):
        if st_text.strip() == "":
            st.error("Source text is required.")
        else:
            if selected_ex=="New":
                existing_ids = [int(k) for k in exercises.keys() if k.isdigit()] if exercises else []
                next_id = str(max(existing_ids)+1 if existing_ids else 1).zfill(3)
            else:
                next_id = selected_ex
            exercises[next_id] = {"source_text": st_text, "mt_text": mt_text if mt_text.strip() else None}
            save_json(EXERCISES_FILE, exercises)
            st.success(f"Exercise saved! ID: {next_id}")

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
    st.markdown(f"<div style='font-family: Times New Roman; font-size:12pt;'>{ex['source_text']}</div>", unsafe_allow_html=True)

    task_options = ["Translate"] if not ex.get("mt_text") else ["Translate", "Post-edit MT"]
    task_type = st.radio("Task Type", task_options)

    initial_text = "" if task_type=="Translate" else ex.get("mt_text","")
    st.subheader("Your Work")
    student_text = st.text_area("Type your translation / post-edit here", initial_text, height=400)

    # Optional: Use MT as reference
    use_mt_as_reference = False
    if ex.get("mt_text"):
        use_mt_as_reference = st.checkbox("Use MT output as reference for metrics", value=False)

    # Timer & keystrokes
    if f"start_time_{ex_id}" not in st.session_state:
        st.session_state[f"start_time_{ex_id}"] = time.time()
    if f"keystrokes_{ex_id}" not in st.session_state:
        st.session_state[f"keystrokes_{ex_id}"] = 0

    if st.button("Submit"):
        time_spent = time.time() - st.session_state[f"start_time_{ex_id}"]
        st.session_state[f"keystrokes_{ex_id}"] = len(student_text)

        # Determine reference
        reference = ex.get("reference_text") or (ex.get("mt_text") if use_mt_as_reference else None)
        metrics = evaluate_translation(ex["source_text"], student_text, reference)

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
        metric_lines = [f"- **{k}:** {v}" for k,v in metrics.items()]
        st.markdown("\n".join(metric_lines))

        st.subheader("Track Changes")
        highlighted = diff_text(ex.get("mt_text","") if task_type=="Post-edit MT" else "", student_text)
        st.markdown(highlighted, unsafe_allow_html=True)

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
