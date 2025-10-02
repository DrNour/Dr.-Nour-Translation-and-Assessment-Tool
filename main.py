import streamlit as st
import json
import os
import difflib
import pandas as pd
from io import BytesIO
from docx import Document

# ----------------------------
# File paths
# ----------------------------
EXERCISES_FILE = "exercises.json"
SUBMISSIONS_FILE = "submissions.json"
POINTS_FILE = "points.json"

# ----------------------------
# Helpers
# ----------------------------
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def diff_text(original, edited):
    differ = difflib.Differ()
    diff = list(differ.compare(original.split(), edited.split()))
    result = []
    for word in diff:
        if word.startswith("- "):
            result.append(f"~~{word[2:]}~~")
        elif word.startswith("+ "):
            result.append(f"**{word[2:]}**")
        else:
            result.append(word[2:])
    return " ".join(result)

# ----------------------------
# Load Data
# ----------------------------
exercises = load_json(EXERCISES_FILE, {})
submissions = load_json(SUBMISSIONS_FILE, {})
points = load_json(POINTS_FILE, {})

# ----------------------------
# Instructor Dashboard
# ----------------------------
def instructor_dashboard():
    st.sidebar.subheader("Instructor Dashboard")
    choice = st.sidebar.radio("Menu", ["Create/Edit Exercise", "Review Submissions", "Leaderboard"])

    if choice == "Create/Edit Exercise":
        st.title("📘 Manage Exercises")

        with st.form("exercise_form"):
            title = st.text_input("Exercise Title")
            source_text = st.text_area("Source Text")
            reference_translation = st.text_area("Reference Translation (optional)")
            submitted = st.form_submit_button("Save Exercise")

        if submitted and title:
            exercises[title] = {
                "source_text": source_text,
                "reference": reference_translation,
            }
            save_json(exercises, EXERCISES_FILE)
            st.success(f"Exercise '{title}' saved!")

        if exercises:
            st.subheader("Existing Exercises")
            for ex in list(exercises.keys()):
                col1, col2 = st.columns([3,1])
                col1.write(ex)
                if col2.button("❌ Delete", key=ex):
                    del exercises[ex]
                    save_json(exercises, EXERCISES_FILE)
                    st.warning(f"Exercise '{ex}' deleted.")
                    st.experimental_rerun()

    elif choice == "Review Submissions":
        st.title("📑 Review Submissions")

        if not submissions:
            st.info("No submissions yet.")
            return

        student_choice = st.selectbox("Choose a student", list(submissions.keys()))
        assignment_choice = st.selectbox("Choose an exercise", list(submissions[student_choice].keys()))
        data = submissions[student_choice][assignment_choice]

        st.write("### Source Text")
        st.info(data["source_text"])

        st.write("### Student Translation")
        st.write(data["student_translation"])

        instructor_edit = st.text_area("✏️ Instructor Post-Editing", data["student_translation"])
        if st.button("Save Post-Editing"):
            submissions[student_choice][assignment_choice]["post_editing"] = instructor_edit
            submissions[student_choice][assignment_choice]["diff"] = diff_text(
                data["student_translation"], instructor_edit
            )
            save_json(submissions, SUBMISSIONS_FILE)
            st.success("✅ Post-editing saved!")

        if "post_editing" in data:
            st.write("### Instructor Post-Editing")
            st.write(data["post_editing"])
            st.write("### Track Changes")
            st.markdown(data["diff"], unsafe_allow_html=True)

            # Export to Word
            doc = Document()
            doc.add_heading("Translation Review", level=1)
            doc.add_paragraph(f"Student: {student_choice}")
            doc.add_paragraph(f"Exercise: {assignment_choice}")
            doc.add_heading("Source Text", level=2)
            doc.add_paragraph(data["source_text"])
            doc.add_heading("Student Translation", level=2)
            doc.add_paragraph(data["student_translation"])
            doc.add_heading("Instructor Post-Editing", level=2)
            doc.add_paragraph(data["post_editing"])
            doc.add_heading("Track Changes", level=2)
            doc.add_paragraph(data["diff"])

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="📥 Download as Word Document",
                data=buffer,
                file_name=f"{student_choice}_{assignment_choice}_review.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        # Export summary to Excel
        if st.button("📊 Download Excel Summary"):
            rows = []
            for stu, stu_subs in submissions.items():
                for ex, details in stu_subs.items():
                    rows.append({
                        "Student": stu,
                        "Exercise": ex,
                        "Translation": details.get("student_translation", ""),
                        "Post-editing": details.get("post_editing", ""),
                    })
            df = pd.DataFrame(rows)
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)
            st.download_button(
                "Download Submissions Excel",
                data=buffer,
                file_name="submissions_summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    elif choice == "Leaderboard":
        st.title("🏆 Leaderboard")
        if points:
            df = pd.DataFrame(points.items(), columns=["Student", "Points"]).sort_values(by="Points", ascending=False)
            st.table(df)
        else:
            st.info("No points yet.")

# ----------------------------
# Student Dashboard
# ----------------------------
def student_dashboard():
    st.sidebar.subheader("Student Dashboard")
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

    translation = st.text_area("✍️ Your Translation")
    if st.button("Submit Translation"):
        if student_name not in submissions:
            submissions[student_name] = {}
        submissions[student_name][assignment] = {
            "source_text": exercises[assignment]["source_text"],
            "student_translation": translation
        }
        save_json(submissions, SUBMISSIONS_FILE)

        # Award points
        points[student_name] = points.get(student_name, 0) + 10
        save_json(points, POINTS_FILE)

        st.success("✅ Translation submitted! You earned 10 points.")

# ----------------------------
# Main App
# ----------------------------
def main():
    st.sidebar.title("Translation & Assessment Tool")
    mode = st.sidebar.radio("Login as", ["Student", "Instructor"])
    if mode == "Instructor":
        instructor_dashboard()
    else:
        student_dashboard()

if __name__ == "__main__":
    main()
