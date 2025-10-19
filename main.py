import streamlit as st
import json
import os
import time
import re
import random
import threading
from pathlib import Path
from typing import List, Tuple
from difflib import SequenceMatcher, ndiff
from io import BytesIO

import requests  # used by ai_generate_text
import pandas as pd
from docx import Document
from docx.shared import RGBColor

# Optional metrics deps (graceful fallback if missing)
try:
    import sacrebleu
except Exception:
    sacrebleu = None

try:
    from bert_score import score as bertscore_score
except Exception:
    bertscore_score = None

# ---------------- Storage (JSON with basic locking & atomic writes) ----------------
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

EXERCISES_FILE = DATA_DIR / "exercises.json"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"

_lock = threading.Lock()

def load_json(file: Path):
    file = Path(file)
    if file.exists():
        with file.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # If a previous run got interrupted; return empty dict rather than crashing
                return {}
    return {}

def save_json(file: Path, data):
    with _lock:
        tmp = Path(str(file) + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        tmp.replace(file)

# ---------------- Tokenization & Edit Helpers ----------------
_token_re = re.compile(r"\w+|[^\w\s]", re.UNICODE)

def _tokenize(s: str) -> List[str]:
    return _token_re.findall(s or "")

def compute_edit_details(mt_text: str, student_text: str) -> Tuple[int, int, int]:
    """
    Token-level edit summary:
    additions, deletions, total_edits
    (replace counts as max span length, i.e., single op per replaced region)
    """
    mt_tokens = _tokenize(mt_text)
    st_tokens = _tokenize(student_text)
    matcher = SequenceMatcher(None, mt_tokens, st_tokens)

    additions = deletions = replacements = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            additions += (j2 - j1)
        elif tag == "delete":
            deletions += (i2 - i1)
        elif tag == "replace":
            replacements += max(i2 - i1, j2 - j1)
    total_edits = additions + deletions + replacements
    return additions, deletions, total_edits

# ---------------- Metrics ----------------
def evaluate_translation(student_text, mt_text=None, reference=None, task_type="Translate", source_text=""):
    """
    Returns a metrics dict using:
      - length_ratio (target tokens / source tokens)
      - BLEU (sacrebleu, if reference provided)
      - chrF++ (sacrebleu, if reference provided)
      - BERTScore_F1 (if available & reference provided)
      - edit counts for post-edit tasks
    All metrics gracefully fallback to None if libs or references are missing.
    """
    src_len = max(1, len(_tokenize(source_text)))
    tgt_len = len(_tokenize(student_text))
    length_ratio = round(tgt_len / src_len, 3)

    if task_type == "Post-edit MT" and mt_text:
        additions, deletions, edits = compute_edit_details(mt_text, student_text)
    else:
        additions = deletions = edits = 0

    bleu = chrf = bert_f1 = None
    if reference:
        refs = [reference]
        try:
            if sacrebleu:
                # sacrebleu expects: sys_stream (list[str]), ref_streams (list[list[str]])
                bleu = float(sacrebleu.corpus_bleu([student_text], [refs]).score)  # 0-100
                chrf = float(sacrebleu.corpus_chrf([student_text], [refs]).score)  # 0-100
        except Exception:
            bleu = None
            chrf = None

        try:
            if bertscore_score:
                P, R, F1 = bertscore_score([student_text], [reference], lang="en")
                bert_f1 = float(F1.mean().item())  # 0-1
        except Exception:
            bert_f1 = None

    return {
        "length_ratio": length_ratio,
        "BLEU": None if bleu is None else round(bleu, 2),
        "chrF++": None if chrf is None else round(chrf, 2),
        "BERTScore_F1": None if bert_f1 is None else round(bert_f1, 3),
        "additions": additions,
        "deletions": deletions,
        "edits": edits
    }

# ---------------- Track Changes (HTML + DOCX) ----------------
def _join_tokens_for_display(tokens: List[str]) -> str:
    # Join tokens with spaces, then clean spaces before punctuation
    out = " ".join(tokens)
    out = re.sub(r"\s+([.,!?;:])", r"\1", out)
    return out

def diff_text(baseline: str, student_text: str) -> str:
    differ = ndiff(_tokenize(baseline), _tokenize(student_text))
    parts = []
    for w in differ:
        token = w[2:]
        if w.startswith("- "):
            parts.append(f"<span style='color:#c00;text-decoration:line-through'>{token}</span>")
        elif w.startswith("+ "):
            parts.append(f"<span style='color:#080'>{token}</span>")
        else:
            parts.append(token)
    return _join_tokens_for_display(parts)

def add_diff_to_doc(doc: Document, baseline: str, student_text: str):
    differ = ndiff(_tokenize(baseline), _tokenize(student_text))
    p = doc.add_paragraph()
    for w in differ:
        token = w[2:]
        if w.startswith("- "):
            run = p.add_run(token + " ")
            run.font.strike = True
            run.font.color.rgb = RGBColor(255, 0, 0)
        elif w.startswith("+ "):
            run = p.add_run(token + " ")
            run.font.color.rgb = RGBColor(0, 128, 0)
        else:
            p.add_run(token + " ")

# ---------------- Word Export ----------------
def export_student_word(submissions, student_name):
    doc = Document()
    doc.add_heading(f"Student: {student_name}", 0)
    subs = submissions.get(student_name, {})
    for ex_id, sub in subs.items():
        doc.add_heading(f"Exercise {ex_id}", level=1)
        doc.add_paragraph("Source Text:")
        doc.add_paragraph(sub.get("source_text", ""))
        if sub.get("mt_text"):
            doc.add_paragraph("MT Output:")
            doc.add_paragraph(sub.get("mt_text", ""))

        # Student submission (with or without track changes)
        if sub.get("task_type") == "Post-edit MT":
            doc.add_paragraph("Student Submission (Track Changes):")
            base = sub.get("mt_text", "") or ""
            add_diff_to_doc(doc, base, sub.get("student_text", ""))
        else:
            doc.add_paragraph("Student Submission:")
            doc.add_paragraph(sub.get("student_text", ""))

        metrics = sub.get("metrics", {})
        doc.add_paragraph(f"Metrics: {metrics}")
        doc.add_paragraph(f"Task Type: {sub.get('task_type','')}")
        doc.add_paragraph(f"Time Spent: {sub.get('time_spent_sec', 0):.2f} sec")
        doc.add_paragraph(f"Characters (not keystrokes): {sub.get('keystrokes', 0)}")
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
            m = sub.get("metrics", {})
            rows.append({
                "Student": student,
                "Exercise": ex_id,
                "Task Type": sub.get("task_type", ""),
                "Length Ratio": m.get("length_ratio"),
                "BLEU": m.get("BLEU"),
                "chrF++": m.get("chrF++"),
                "BERTScore_F1": m.get("BERTScore_F1"),
                "Additions": m.get("additions"),
                "Deletions": m.get("deletions"),
                "Edits": m.get("edits"),
                "Time Spent (s)": sub.get("time_spent_sec", 0),
                "Characters Typed": sub.get("keystrokes", 0)
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
    st.subheader("Leaderboard")
    if leaderboard:
        # Show as dataframe for clarity
        items = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        df = pd.DataFrame(items, columns=["Student", "Points"])
        st.dataframe(df, use_container_width=True)
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
        response = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers=headers,
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return data[0]["generated_text"]
    except Exception:
        pass
    return None

# ---------------- Instructor ----------------
def instructor_dashboard():
    st.title("Instructor Dashboard")
    # Per your request, leave password as-is:
    password = st.text_input("Enter instructor password", type="password")
    if password != "admin123":
        st.warning("Incorrect password. Access denied.")
        return

    exercises = load_json(EXERCISES_FILE)
    submissions = load_json(SUBMISSIONS_FILE)

    st.subheader("Create / Edit / Delete Exercise")
    ex_ids = ["New"] + list(exercises.keys())
    selected_ex = st.selectbox("Select Exercise", ex_ids)

    # Prefill if editing
    if selected_ex != "New":
        default_source = exercises[selected_ex]["source_text"]
        default_mt = exercises[selected_ex].get("mt_text", "") or ""
    else:
        default_source = ""
        default_mt = ""

    with st.form("exercise_form"):
        st_text = st.text_area("Source Text", value=default_source, height=150)
        mt_text = st.text_area("MT Output (optional)", value=default_mt, height=150)
        col1, col2, col3 = st.columns(3)
        with col1:
            save_btn = st.form_submit_button("Save Exercise")
        with col2:
            delete_btn = st.form_submit_button("Delete Exercise")
        with col3:
            gen_btn = st.form_submit_button("Generate AI Exercise")

    if save_btn:
        next_id = (
            str(max([int(k) for k in exercises.keys()] + [0]) + 1).zfill(3)
            if selected_ex == "New" else selected_ex
        )
        exercises[next_id] = {
            "source_text": st_text,
            "mt_text": (mt_text.strip() or None)
        }
        save_json(EXERCISES_FILE, exercises)
        st.success(f"Exercise saved! ID: {next_id}")

    if delete_btn and selected_ex != "New":
        exercises.pop(selected_ex, None)
        save_json(EXERCISES_FILE, exercises)
        st.success(f"Exercise {selected_ex} deleted!")

    if gen_btn:
        prompt = "Write a short culturally rich text for translation students."
        ai_text = ai_generate_text(prompt)
        new_text = ai_text if ai_text else f"This is AI generated exercise {random.randint(1,1000)}."
        new_mt = f"MT output for exercise {random.randint(1,1000)}."
        next_id = str(max([int(k) for k in exercises.keys()] + [0]) + 1).zfill(3)
        exercises[next_id] = {"source_text": new_text, "mt_text": new_mt}
        save_json(EXERCISES_FILE, exercises)
        st.success(f"Exercise saved as ID {next_id}")

    st.subheader("Download Exercises")
    if exercises:
        for ex_id, ex in exercises.items():
            buf = BytesIO()
            doc = Document()
            doc.add_heading(f"Exercise {ex_id}", 0)
            doc.add_paragraph("Source Text:")
            doc.add_paragraph(ex.get("source_text", ""))
            if ex.get("mt_text"):
                doc.add_paragraph("MT Output:")
                doc.add_paragraph(ex.get("mt_text", ""))
            doc.save(buf)
            buf.seek(0)
            st.download_button(
                f"Exercise {ex_id} (Word)",
                buf,
                file_name=f"Exercise_{ex_id}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.info("No exercises yet.")

    st.subheader("Student Submissions & Exports")
    if submissions:
        student_choice = st.selectbox("Choose student", ["All"] + list(submissions.keys()))
        if student_choice != "All":
            buf = export_student_word(submissions, student_choice)
            safe_name = re.sub(r"[^\w\-]+", "_", student_choice)
            st.download_button(
                f"Download {student_choice}'s Submissions (Word)",
                buf,
                file_name=f"{safe_name}_submissions.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        st.subheader("Download Metrics Summary (Excel)")
        excel_buf = export_summary_excel(submissions)
        st.download_button(
            "Download Excel Summary",
            excel_buf,
            file_name="metrics_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        show_leaderboard()
    else:
        st.info("No submissions yet.")

# ---------------- Student ----------------
def student_dashboard():
    st.title("Student Dashboard")

    exercises = load_json(EXERCISES_FILE)
    if not exercises:
        st.info("No exercises available yet. Please check back later.")
        return

    submissions = load_json(SUBMISSIONS_FILE)
    student_name = st.text_input("Enter your name")
    if not student_name:
        return

    # Ensure per-student container in JSON
    if student_name not in submissions:
        submissions[student_name] = {}

    ex_id = st.selectbox("Choose Exercise", list(exercises.keys()))
    if not ex_id:
        return

    ex = exercises[ex_id]
    st.subheader("Source Text")
    st.markdown(
        f"<div style='font-family:Times New Roman;font-size:12pt;'>{ex.get('source_text','')}</div>",
        unsafe_allow_html=True
    )

    task_options = ["Translate"] if not ex.get("mt_text") else ["Translate", "Post-edit MT"]
    task_type = st.radio("Task Type", task_options, horizontal=True)

    initial_text = "" if task_type == "Translate" else (ex.get("mt_text", "") or "")

    # Session keys unique per student/exercise
    start_key = f"start_time_{student_name}_{ex_id}"
    keys_key = f"chars_{student_name}_{ex_id}"
    if start_key not in st.session_state:
        st.session_state[start_key] = time.time()
    if keys_key not in st.session_state:
        st.session_state[keys_key] = 0

    with st.form(key=f"exercise_form_{student_name}_{ex_id}"):
        student_text = st.text_area(
            "Type your translation / post-edit here",
            initial_text,
            height=300
        )
        submitted = st.form_submit_button("Submit")

    if submitted:
        time_spent = time.time() - st.session_state[start_key]
        st.session_state[keys_key] = len(student_text)  # characters typed proxy

        # NOTE: reference is not provided in this app; pass None unless you add a gold reference
        metrics = evaluate_translation(
            student_text,
            mt_text=ex.get("mt_text"),
            reference=None,  # plug in a gold reference string here if available
            task_type=task_type,
            source_text=ex.get("source_text", "")
        )

        # Persist submission
        submissions[student_name][ex_id] = {
            "source_text": ex.get("source_text", ""),
            "mt_text": ex.get("mt_text"),
            "student_text": student_text,
            "task_type": task_type,
            "time_spent_sec": round(time_spent, 2),
            "keystrokes": st.session_state[keys_key],  # actually characters
            "metrics": metrics
        }
        save_json(SUBMISSIONS_FILE, submissions)

        # Gamification points (BLEU/chrF++ might be None if no reference)
        points = 0
        if metrics.get("BLEU") is not None:
            points += int(metrics["BLEU"])
        if metrics.get("chrF++") is not None:
            points += int(metrics["chrF++"] / 2)  # chrF++ is 0-100; dampen
        if task_type == "Post-edit MT":
            # reward efficient editing (fewer edits)
            points += max(0, 10 - int(metrics["edits"]))
        update_leaderboard(student_name, points)

        st.success("Submission saved!")

        # Show metrics neatly
        st.subheader("Your Metrics")
        def _fmt(v):
            return "—" if v is None else v
        st.markdown(f"""
- **Length Ratio** (target/src): {_fmt(metrics['length_ratio'])}
- **BLEU**: {_fmt(metrics['BLEU'])}
- **chrF++**: {_fmt(metrics['chrF++'])}
- **BERTScore F1**: {_fmt(metrics['BERTScore_F1'])}
- **Additions**: {_fmt(metrics['additions'])}
- **Deletions**: {_fmt(metrics['deletions'])}
- **Edits**: {_fmt(metrics['edits'])}
- **Time Spent**: {round(time_spent, 2)} sec
- **Characters Typed**: {st.session_state[keys_key]}
""")

        if task_type == "Post-edit MT":
            st.subheader("Track Changes")
            base = ex.get("mt_text", "") or ""
            st.markdown(diff_text(base, student_text), unsafe_allow_html=True)

        show_leaderboard()

# ---------------- Main ----------------
def main():
    st.set_page_config(page_title="Translation Lab", layout="wide")
    st.sidebar.title("Navigation")
    role = st.sidebar.radio("Login as", ["Instructor", "Student"], index=1)
    if role == "Instructor":
        instructor_dashboard()
    else:
        student_dashboard()

if __name__ == "__main__":
    main()
