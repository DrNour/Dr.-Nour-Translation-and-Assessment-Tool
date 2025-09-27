import streamlit as st

def student_dashboard():
    st.subheader("Student Dashboard")
    st.info("Student features are available here.")
    st.text_area("Translate here:")
    st.button("Submit Translation")
