# modules/instructor_interface.py
import streamlit as st

def instructor_dashboard():
    st.subheader("Instructor Dashboard")
    st.info("Create exercises and download student submissions here.")

    # Dummy exercise creation
    exercise_text = st.text_area("Enter exercise text:")
    if st.button("Create Exercise"):
        st.success("Exercise created!")

    # Dummy download
    if st.button("Download Submissions"):
        st.download_button("Download CSV", data="student1,student2", file_name="submissions.csv")
