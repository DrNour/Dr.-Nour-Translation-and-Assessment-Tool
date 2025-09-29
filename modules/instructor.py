import streamlit as st
import uuid
from modules import storage

def instructor_dashboard():
    st.title("📘 Instructor Dashboard")

    # Create Assignment
    st.subheader("Create New Assignment")
    title = st.text_input("Assignment Title")
    text = st.text_area("Assignment Text")
    instructions = st.text_area("Instructions")
    group = st.selectbox("Assign to Group", ["all", "Group A", "Group B", "Group C"])

    if st.button("Save Assignment"):
        if title.strip() and text.strip():
            assignments = storage.load_assignments()
            assignment_id = str(uuid.uuid4())
            assignments[assignment_id] = {
                "id": assignment_id,
                "title": title,
                "text": text,
                "instructions": instructions,
                "group": group
            }
            storage.save_assignments(assignments)
            st.success(f"Assignment '{title}' created successfully!")

    # Existing Assignments
    st.subheader("📂 Existing Assignments")
    assignments = storage.load_assignments()
    if assignments:
        for a in assignments.values():
            st.write(f"**{a['title']}** (Group: {a['group']})")
            st.write(a.get("instructions", ""))
            st.write(a.get("text", ""))
            st.markdown("---")
    else:
        st.info("No assignments yet.")

    # Student Submissions
    st.subheader("📥 Student Submissions")
    submissions = storage.load_submissions()
    if submissions:
        for s in submissions.values():
            st.write(f"**{s['student_name']}** ({s['group']}) - {s['assignment_title']}")
            st.write(f"✍️ {s['translation']}")
            st.markdown("---")
    else:
        st.info("No submissions yet.")
