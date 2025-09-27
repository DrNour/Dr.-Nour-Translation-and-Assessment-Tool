import streamlit as st

def instructor_dashboard():
    st.header("Instructor Dashboard")
    st.subheader("Create Exercise")
    exercise_text = st.text_area("Enter source text for exercise")
    if st.button("Save Exercise"):
        st.success("Exercise saved!")
    st.subheader("Download Submissions")
    st.button("Download all submissions")
