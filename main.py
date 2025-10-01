import streamlit as st
import json
import os
import time
from difflib import SequenceMatcher
from io import BytesIO
from docx import Document
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

    return {
        "fluency": round(fluency,2),
        "accuracy": round(accuracy,2),
        "additions": additions,
        "omissions": omissions,
        "edits": edits,
        "bleu": None,
        "chrF": None
    }

# ---------------- Track Changes ----------------
def track_changes_html(mt_text, student_text):
    if not mt_text:
        return "No MT output provided."
    mt_words = mt_text.split()
    student_words = student_text.split()
    s = SequenceMatcher(None, mt_words, student_words)
    html_result = []
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'equal':
            html_result.append(" ".join(mt_words[i1:i2]))
        elif tag == 'replace':
            html_result.append(f"<span style='background-color:orange'>{' '.join(mt_words[i1:i2])} → {' '.join(student_words[j1:j2])}</span>")
        elif tag == 'insert':
            html_result.append(f"<span style='background-color:lightgreen'>+{' '.join(student_words[j1:j2])}</span>")
        elif tag == 'delete':
            html_result.append(f"<span style='background-color:salmon'>-{' '.join(mt_words[i1:i2])}</span>")
    return " ".join(html_result)

# ---------------- Student Dashboard ----------------
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

    if not exercises:
        st.info("No exercises available yet.")
        return

    ex_id = st.selectbox("Choose Exercise", list(exercises.keys()))
    ex = exercises[ex_id]

    st.subheader("Source Text")
    st.markdown(f"<div style='font-family: Times New Roman; font-size:14px'>{ex['source_text']}</div>", unsafe_allow_html=True)

    task_options = ["Translate"] if not ex.get("mt_text") else ["Translate", "Post-edit MT"]
    task_type = st.radio("Task Type", task_options)
    initial_text = "" if task_type=="Translate" else ex.get("mt_text","")

    st.subheader("Your Work")
    student_text = st.text_area("Type your translation / post-edit here", initial_text, height=400)

    # Timer & keystrokes
    if f"start_time_{ex_id}" not in st.session_state:
        st.session_state[f"start_time_{ex_id}"] = time.time()
    if f"keystrokes_{ex_id}" not in st.session_state:
        st.session_state[f"keystrokes_{ex_id}"] = 0

    if st.button("Submit"):
        if student_text.strip() == "":
            st.error("Please enter your translation/post-edit.")
            return
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

        # Track Changes preview
        if task_type == "Post-edit MT" and ex.get("mt_text"):
            with st.expander("View Track Changes vs MT"):
                st.markdown(track_changes_html(ex["mt_text"], student_text), unsafe_allow_html=True)

# ---------------- Instructor Dashboard ----------------
def instructor_dashboard():
    st.title("Instructor Dashboard")
    exercises = load_json(EXERCISES_FILE)
    submissions = load_json(SUBMISSIONS_FILE)

    st.subheader("Manage Exercises")
    if exercises:
        for ex_id, ex in exercises.items():
            st.markdown(f"**Exercise {ex_id}**")
            col1, col2, col3 = st.columns([6,1,1])
            with col1:
                st.markdown(f"Source: {ex['source_text'][:100]}{'...' if len(ex['source_text'])>100 else ''}")
            with col2:
                if st.button(f"Edit {ex_id}"):
                    new_source = st.text_area(f"Edit Source Text {ex_id}", ex['source_text'], key=f"src_{ex_id}")
                    new_mt = st.text_area(f"Edit MT Text {ex_id}", ex.get("mt_text",""), key=f"mt_{ex_id}")
                    if st.button(f"Save Edit {ex_id}"):
                        exercises[ex_id]['source_text'] = new_source
                        exercises[ex_id]['mt_text'] = new_mt if new_mt.strip() else None
                        save_json(EXERCISES_FILE, exercises)
                        st.success(f"Exercise {ex_id} updated!")
            with col3:
                if st.button(f"Delete {ex_id}"):
                    del exercises[ex_id]
                    for student in submissions:
                        if ex_id in submissions[student]:
                            del submissions[student][ex_id]
                    save_json(EXERCISES_FILE, exercises)
                    save_json(SUBMISSIONS_FILE, submissions)
                    st.warning(f"Exercise {ex_id} deleted!")

    st.subheader("Student Submissions")
    if not submissions:
        st.info("No submissions yet.")
        return

    student_choice = st.selectbox("Select student", ["All"] + list(submissions.keys()))
    selected_students = [student_choice] if student_choice != "All" else submissions.keys()
    show_full_text = st.checkbox("Show full submission text in app", value=False)

    rows = []
    for student in selected_students:
        st.markdown(f"### Student: {student}")
        for ex_id, sub in submissions[student].items():
            st.markdown(f"**Exercise {ex_id}**")
            if show_full_text:
                st.markdown(f"**Source:** {sub['source_text']}")
                if sub.get("mt_text"):
                    st.markdown(f"**MT Output:** {sub['mt_text']}")
                st.markdown(f"**Student Submission:** {sub['student_text']}")
            metrics = sub.get("metrics", {})
            st.markdown(f"**Metrics:** {metrics}")

            if sub.get("task_type")=="Post-edit MT" and sub.get("mt_text"):
                with st.expander("View Track Changes"):
                    st.markdown(track_changes_html(sub["mt_text"], sub["student_text"]), unsafe_allow_html=True)

            rows.append({
                "student": student,
                "exercise_id": ex_id,
                "source_text": sub["source_text"],
                "mt_text": sub.get("mt_text"),
                "student_text": sub["student_text"],
                "task_type": sub.get("task_type"),
                **metrics,
                "time_spent_sec": sub.get("time_spent_sec"),
                "keystrokes": sub.get("keystrokes")
            })

    if rows:
        df = pd.DataFrame(rows)
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download All Submissions (CSV)", csv_data, file_name="submissions_summary.csv", mime="text/csv")

        if st.button("📥 Download Word Reports"):
            for student in selected_students:
                doc = Document()
                doc.add_heading(f"Student: {student}", 0)
                for ex_id, sub in submissions[student].items():
                    doc.add_heading(f"Exercise {ex_id}", level=1)
                    doc.add_paragraph(f"Source Text:\n{sub['source_text']}")
                    if sub.get("mt_text"):
                        doc.add_paragraph(f"MT Output:\n{sub['mt_text']}")
                    doc.add_paragraph(f"Student Submission:\n{sub['student_text']}")
                    doc.add_paragraph(f"Metrics: {sub.get('metrics',{})}")
                    doc.add_paragraph(f"Task Type: {sub.get('task_type','')}")
                    doc.add_paragraph(f"Time Spent: {sub.get('time_spent_sec',0):.2f} sec")
                    doc.add_paragraph(f"Keystrokes: {sub.get('keystrokes',0)}")
                    doc.add_paragraph("---")
                buf = BytesIO()
                doc.save(buf)
                buf.seek(0)
                st.download_button(f"Download Word Report {student}", buf, file_name=f"{student}_report.docx")

    # ---------------- Lightweight Gamification ----------------
    with st.expander("Gamification / Points (Optional)"):
        if rows:
            gamification = []
            for student in selected_students:
                student_rows = [r for r in rows if r['student']==student]
                total_points = 0
                for r in student_rows:
                    flu = r.get('fluency',0)
                    acc = r.get('accuracy',0)
                    points = round(((flu + acc)/2)*100)
                    total_points += points
                avg_points = round(total_points/len(student_rows)) if student_rows else 0
                if avg_points >= 90:
                    badge = "🏆 Gold"
                elif avg_points >= 75:
                    badge = "🥈 Silver"
                elif avg_points >= 60:
                    badge = "🥉 Bronze"
                else:
                    badge = "📝 Keep Practicing"
                gamification.append({"student": student, "points": avg_points, "badge": badge})
            df_gaming = pd.DataFrame(gamification)
            st.dataframe(df_gaming.sort_values(by="points", ascending=False))

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
