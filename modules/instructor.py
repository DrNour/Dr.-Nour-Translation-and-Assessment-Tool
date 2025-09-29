import streamlit as st
import uuid
from utils.storage import load_assignments, save_assignments, load_submissions

def instructor_dashboard():
    st.header("📘 Instructor Dashboard")

    # ---- Create Assignment ----
    st.subheader("Create New Assignment")
    title = st.text_input("Assignment Title")
    instructions = st.text_area("Instructions")
    exercise_text = st.text_area("Exercise Text")
    group = st.selectbox("Assign to Group", ["all", "Group A", "Group B", "Group C"])

    if st.button("Save Assignment"):
        assignments = load_assignments()
        assignment_id = str(uuid.uuid4())
        assignments[assignment_id] = {
            "id": assignment_id,
            "title": title,
            "instructions": instructions,
            "exercise_text": exercise_text,
            "group": group,
        }
        save_assignments(assignments)
        st.success("✅ Assignment saved successfully!")

    # ---- List Assignments ----
    st.subheader("📂 Existing Assignments")
    assignments = load_assignments()
    if assignments:
        for a in assignments.values():
            st.markdown(f"**{a['title']}**  \n_Group: {a['group']}_  \n📖 {a['instructions']}  \n✍️ {a['exercise_text']}")
            st.markdown("---")
    else:
        st.info("No assignments created yet.")

    # ---- Review Submissions ----
    st.subheader("📥 Student Submissions")
    submissions = load_submissions()
    if submissions:
        for s in submissions.values():
            st.markdown(f"**{s['student_name']}** ({s['group']}) - {s['assignment_title']}  \n✍️ {s['translation']}")
            st.markdown("---")
    else:
        st.info("No submissions yet.")
