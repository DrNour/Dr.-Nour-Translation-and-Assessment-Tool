import streamlit as st

def student_dashboard():
    st.subheader("🎓 Student Dashboard")
    st.text_area("Source Text", "Enter your translation here...")
    mode = st.radio("Mode:", ["Translate from Scratch", "Post-Edit MT Output"])
    st.text_area("Your Translation")
    st.button("Submit Translation")
