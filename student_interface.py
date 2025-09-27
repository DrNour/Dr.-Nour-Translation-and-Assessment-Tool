# student_interface.py
import streamlit as st

def run_feature():
    st.header("Student Interface")
    
    st.subheader("Submit Translation")
    translation_text = st.text_area("Your Translation")
    reference_text = st.text_area("Optional Reference Text")
    
    translate_type = st.radio("Choose Translation Mode", ["Translate from Scratch", "Post-Edit Translation"])
    
    if st.button("Submit Translation"):
        if not translation_text:
            st.warning("Translation text cannot be empty.")
        else:
            # TODO: Save student submission
            st.success("Submission received! (placeholder)")
    
    st.subheader("Gamification & Leaderboard")
    st.info("Points, badges, and leaderboard will be displayed here (placeholder).")
