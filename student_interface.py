import streamlit as st

def student_dashboard():
    st.header("Student Dashboard")
    st.subheader("Submit Translation")
    translation = st.text_area("Enter your translation here")
    reference = st.text_area("Optional reference translation")
    if st.button("Submit"):
        st.success("Submitted!")
