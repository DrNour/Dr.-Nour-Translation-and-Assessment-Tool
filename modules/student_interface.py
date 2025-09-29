import streamlit as st
from utils.storage import load_assignments, load_submissions, save_submissions

def student_dashboard():
    st.title("Student Dashboard")

    assignments = load_assignments()

    if not assignments:
        st.info("No assignments available yet.")
        return

    selected = st.selectbox("Choose an assignment", list(assignments.keys()))
    st.write("### Assignment Text")
    st.write(assignments[selected]["text"])

    translation = st.text_area("Enter your translation here")

    if st.button("Submit Translation"):
        save_submissions(selected, translation)
        st.success("Your translation has been submitted!")

    submissions = load_submissions()
    if submissions:
        st.subheader("Your Previous Submissions")
        for task, sub in submissions.items():
            st.write(f"**{task}**: {sub}")
