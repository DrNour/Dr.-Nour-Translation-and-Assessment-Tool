import streamlit as st
import json
import os
import time
from difflib import SequenceMatcher, ndiff
from io import BytesIO
from docx import Document
import pandas as pd

# ----------------------------
# File paths
# ----------------------------
EXERCISES_FILE = "exercises.json"
SUBMISSIONS_FILE = "submissions.json"
POINTS_FILE = "points.json"

# ----------------------------
# Helpers
# ----------------------------
def load_json(file, default={}):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Metrics calculation
def evaluate_translation(baseline_text, student_text, reference=None):
    fluency = len(student_text.split()) / (len(baseline_text.split()) + 1)
    accuracy = SequenceMatcher(None, baseline_text, student_text).ratio()

    additions = deletions = edits = 0
    sm = SequenceMatcher(None, baseline_text.split(), student_text.split())
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "insert":
            additions += j2 - j1
        elif tag == "delete":
            deletions += i2 - i1
        elif tag == "replace":
            edits += max(i2 - i1, j2 - j1)

    bleu = chrf = None
    if reference:
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

    return {
        "fluency": round(fluency,2),
        "accuracy": round(accuracy,2),
        "bleu": round(bleu,2) if bleu is not None else None,
        "chrF": round(chrf,2) if chrf is not None else None,
        "additions": additions,
        "deletions": deletions,
        "edits": edits
    }

# Track changes highlighting
def diff_text(baseline, student_text):
    differ = ndiff(baseline.split(), student_text.split())
    result = []
    for w in differ:
        if w.startswith("- "):
            result.append(f"~~{w[2:]}~~")
        elif w.startswith("+ "):
            result.append(f"**{w[2:]}**")
        else:
            result.append(w[2:])
    return " ".join(result)

# ----------------------------
# Load Data
# ----------------------------
exercises = load_json(EXERCISES_FILE)
submissions = load_json(SUBMISSIONS_FILE)
points = load_json(POINTS_FILE)

# ----------------------------
# Word export
# ----------------------------
def export_student_word(student_name, student_data):
    doc = Document()
    doc.add_heading(f"Student: {student_name}", level=1)
    for ex_id, sub in student_data.items():
        doc.add_heading(f"Exercise: {ex_id}", level=2)
        doc.add_heading("Source Text", level=3)
        doc.add_paragraph(sub["source_text"])
        doc.add_heading("Student Translation / Post-edit", level=3)
        doc.add_paragraph(sub.get("student_translation",""))
        doc.add_heading("Metrics", level=3)
        doc.add_paragraph(str(sub.get("metrics",{})))
        doc.add_heading("Track Changes", level=3)
        doc.add_paragraph(sub.get("diff",""))
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ----------------------------
# Excel summary
# ----------------------------
def export_summary_excel(submissions):
    rows = []
    for student, data in submissions.items():
        for ex_id, sub in data.items():
            metrics = sub.get("metrics", {})
            rows.append({
                "Student": student,
                "Exercise": ex_id,
                "Fluency": metrics.get("fluency"),
                "Accuracy": metrics.get("accuracy"),
                "Additions": metrics.get("additions"),
                "Deletions": metrics.get("deletions"),
                "Edits": metrics.get("edits"),
                "BLEU": metrics.get("bleu"),
                "chrF": metrics.get("chrF")
            })
    df = pd.DataFrame(rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Summary")
    output.seek(0)
    return output

# ----------------------------
# Leaderboard
# ----------------------------
def show_leaderboard():
    st.subheader("🏆 Leaderboard")
    if points:
        df_points = pd.DataFrame([{"Student": s, "Points": p} for s, p in points.items()])
        df_points = df_points.sort_values("Points", ascending=False)
        st.table(df_points)
    else:
        st.info("No points yet.")

# ----------------------------
# Instructor Dashboard
# ----------------------------
def instructor_dashboard():
    st.sidebar.subheader("Instructor Panel")
    choice = st.sidebar.radio("Menu", ["Manage Exercises", "Review Submissions", "Export", "Leaderboard"])

    if choice == "Manage Exercises":
        st.title("📘 Manage Exercises")
        with st.form("exercise_form"):
            title = st.text_input("Exercise Title")
            source_text = st.text_area("Source Text")
            reference_translation = st.text_area("Reference Translation (optional)")
            mt_text = st.text_area("Machine Translation Output (optional)")
            submitted = st.form_submit_button("Save Exercise")
        if submitted and title.strip():
            exercises[title] = {"source_text": source_text, "reference": reference_translation, "mt_text": mt_text}
            save_json(exercises, EXERCISES_FILE)
            st.success(f"Exercise '{title}' saved!")

        if exercises:
            st.subheader("Existing Exercises")
            for ex in list(exercises.keys()):
                with st.expander(ex):
                    data = exercises[ex]
                    new_source = st.text_area("Edit Source Text", data["source_text"], key=ex+"src")
                    new_reference = st.text_area("Edit Reference Translation", data.get("reference",""), key=ex+"ref")
                    new_mt = st.text_area("Edit MT Output", data.get("mt_text",""), key=ex+"mt")
                    if st.button("Save Changes", key=ex+"save"):
                        exercises[ex] = {"source_text": new_source, "reference": new_reference, "mt_text": new_mt}
                        save_json(exercises, EXERCISES_FILE)
                        st.success(f"Exercise '{ex}' updated!")
                    if st.button("❌ Delete Exercise", key=ex+"del"):
                        del exercises[ex]
                        save_json(EXERCISES_FILE, EXERCISES_FILE)
                        st.warning(f"Exercise '{ex}' deleted.")
                        st.experimental_rerun()

    elif choice == "Review Submissions":
        st.title("📑 Review Submissions")
        if not submissions:
            st.info("No submissions yet.")
            return
        student_choice = st.selectbox("Choose a student", list(submissions.keys()))
        student_data = submissions[student_choice]
        for ex_id, sub in student_data.items():
            with st.expander(ex_id):
                st.write("### Source Text")
                st.info(sub["source_text"])
                
                st.write("### Student Translation / Post-edit")
                st.text_area("Student Work", value=sub.get("student_translation",""), height=150)
                
                # Show all metrics including additions/deletions/edits
                st.write("### Metrics")
                metrics = sub.get("metrics", {})
                st.write({
                    "Fluency": metrics.get("fluency"),
                    "Accuracy": metrics.get("accuracy"),
                    "Additions": metrics.get("additions"),
                    "Deletions": metrics.get("deletions"),
                    "Edits": metrics.get("edits"),
                    "BLEU": metrics.get("bleu"),
                    "chrF": metrics.get("chrF")
                })
                
                st.write("### Track Changes")
                diff_html = sub.get("diff","")
                if diff_html:
                    st.markdown(diff_html, unsafe_allow_html=True)
                
                # Optional instructor post-editing
                instructor_edit = st.text_area("Instructor Post-Editing", value=sub.get("post_editing",sub.get("student_translation","")), height=150)
                if st.button("Save Post-Editing", key=ex_id+"edit"):
                    sub["post_editing"] = instructor_edit
                    sub["diff"] = diff_text(sub.get("mt_text",sub.get("student_translation","")), instructor_edit)
                    save_json(submissions, SUBMISSIONS_FILE)
                    st.success("✅ Post-edit saved and diff updated!")

    elif choice == "Export":
        st.title("💾 Export Submissions")
        student_choice = st.selectbox("Select Student for Word Export", ["All"] + list(submissions.keys()))
        if st.button("Export Word"):
            if student_choice=="All":
                for s, data in submissions.items():
                    buf = export_student_word(s, data)
                    st.download_button(f"Download {s}.docx", buf, file_name=f"{s}.docx")
            else:
                buf = export_student_word(student_choice, submissions[student_choice])
                st.download_button(f"Download {student_choice}.docx", buf, file_name=f"{student_choice}.docx")
        if st.button("Export Summary Excel"):
            buf = export_summary_excel(submissions)
            st.download_button("Download Summary.xlsx", buf, file_name="summary.xlsx")

    elif choice == "Leaderboard":
        st.title("📊 Leaderboard")
        show_leaderboard()

# ----------------------------
# Student Dashboard
# ----------------------------
def student_dashboard():
    st.sidebar.subheader("Student Panel")
    student_name = st.sidebar.text_input("Enter your name")
    if not student_name:
        st.warning("Please enter your name.")
        return
    if not exercises:
        st.info("No exercises available yet.")
        return
    assignment = st.selectbox("Choose an exercise", list(exercises.keys()))
    st.write("### Source Text")
    st.info(exercises[assignment]["source_text"])
    baseline = exercises[assignment].get("mt_text","")
    translation = st.text_area("✍️ Your Translation / Post-edit", value=baseline)
    if st.button("Submit Translation"):
        if student_name not in submissions:
            submissions[student_name] = {}
        submissions[student_name][assignment] = {
            "source_text": exercises[assignment]["source_text"],
            "student_translation": translation
        }
        ref = exercises[assignment].get("reference")
        metrics = evaluate_translation(baseline, translation, ref)
        submissions[student_name][assignment]["metrics"] = metrics
        submissions[student_name][assignment]["diff"] = diff_text(baseline, translation)
        save_json(submissions, SUBMISSIONS_FILE)
        points[student_name] = points.get(student_name,0)+10
        save_json(points, POINTS_FILE)
        st.success(f"✅ Translation submitted! You earned 10 points.")
        st.write("### Metrics")
        st.write(metrics)
        st.write("### Track Changes")
        st.markdown(submissions[student_name][assignment]["diff"], unsafe_allow_html=True)
        show_leaderboard()

# ----------------------------
# Main
# ----------------------------
def main():
    st.sidebar.title("Translation & Assessment Tool")
    role = st.sidebar.radio("Login as", ["Student", "Instructor"])
    if role=="Instructor":
        instructor_dashboard()
    else:
        student_dashboard()

if __name__=="__main__":
    main()
