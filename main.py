import streamlit as st
import json
import os
import time
from difflib import SequenceMatcher, ndiff
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
def load_json(file, default={}):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Metrics calculation
def evaluate_translation(st_text, student_text, reference=None):
    fluency = len(student_text.split()) / (len(st_text.split()) + 1)
    accuracy = SequenceMatcher(None, st_text, student_text).ratio()

    bleu = None
    chrf = None
    if reference:
        # BLEU: unigram overlap
        ref_words = reference.split()
        student_words = student_text.split()
        matches = sum(1 for w in student_words if w in ref_words)
        bleu = matches / (len(student_words)+1)

        # chrF: char-level F1
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
        "chrF": round(chrf,2) if chrf is not None else None
    }

# Track changes
def diff_text(original, edited):
    differ = ndiff(original.split(), edited.split())
    result = []
    for word in differ:
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
exercises = load_json(EXERCISES_FILE)
submissions = load_json(SUBMISSIONS_FILE)
points = load_json(POINTS_FILE)

# ----------------------------
# Instructor Dashboard
# ----------------------------
def instructor_dashboard():
    st.sidebar.subheader("Instructor Panel")
    choice = st.sidebar.radio("Menu", ["Manage Exercises", "Review Submissions", "Leaderboard"])

    if choice == "Manage Exercises":
        st.title("📘 Manage Exercises")
        # Create new exercise
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

        # Edit or delete existing exercises
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

        # Show metrics
        ref = exercises.get(assignment_choice, {}).get("reference")
        metrics = evaluate_translation(data["source_text"], data["student_translation"], ref)
        st.write("### Metrics")
        st.write(metrics)

        # Instructor post-editing
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

            # Export Word
            doc = Document()
            doc.add_heading("Translation Review", level=1)
            doc.add_paragraph(f"Student: {student_choice}")
            doc.add_paragraph(f"Exercise: {assignment_choice}")
            doc.add_heading("Source Text", level=2)
            doc.add_paragraph(data["source_text"])
            doc.add_heading("Student Translation", level=2)
            doc.add_paragraph(data["student_translation"])
            doc.add_heading("Metrics", level=2)
            doc.add_paragraph(str(metrics))
            doc.add_heading("Instructor Post-Editing", level=2)
            doc.add_paragraph(data.get("post_editing",""))
            doc.add_heading("Track Changes", level=2)
            doc.add_paragraph(data.get("diff",""))

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button(
                "📥 Download as Word",
                data=buffer,
                file_name=f"{student_choice}_{assignment_choice}_review.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    elif choice == "Leaderboard":
        st.title("🏆 Leaderboard")
        if points:
            leaderboard = sorted(points.items(), key=lambda x: x[1], reverse=True)
            st.table(leaderboard)
        else:
            st.info("No points yet.")

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

    initial_text = exercises[assignment].get("mt_text","")
    translation = st.text_area("✍️ Your Translation / Post-edit", value=initial_text)

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
# Main
# ----------------------------
def main():
    st.sidebar.title("Translation & Assessment Tool")
    role = st.sidebar.radio("Login as", ["Student", "Instructor"])
    if role == "Instructor":
        instructor_dashboard()
    else:
        student_dashboard()

if __name__=="__main__":
    main()
