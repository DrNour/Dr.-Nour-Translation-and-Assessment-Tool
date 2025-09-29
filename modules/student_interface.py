import streamlit as st
import uuid
from utils.storage import load_assignments, load_submissions, save_submissions

def student_dashboard():
    st.header("🎓 Student Dashboard")

    student_name = st.text_input("Enter your name")
    student_group = st.selectbox("Select your group", ["Group A", "Group B", "Group C"])

    if not student_name.strip():
        st.warning("Please enter your name to continue.")
        return

    assignments = load_assignments()
    submissions = load_submissions()

    if assignments:
        for a in assignments.values():
            if a["group"] == "all" or a["group"] == student_group:
                st.subheader(a["title"])
                st.write("📖 Instructions:", a["instructions"])
                st.write("✍️ Exercise:", a["exercise_text"])

                translation = st.text_area(f"Your Answer for {a['title']}", key=a["id"])

                if st.button(f"Submit {a['id']}", key=f"btn_{a['id']}"):
                    submission_id = str(uuid.uuid4())
                    submissions[submission_id] = {
                        "id": submission_id,
                        "assignment_id": a["id"],
                        "assignment_title": a["title"],
                        "student_name": student_name,
                        "group": student_group,
                        "translation": translation,
                    }
                    save_submissions(submissions)
                    st.success(f"✅ {student_name}, your submission has been saved!")
    else:
        st.info("No assignments available yet.")
