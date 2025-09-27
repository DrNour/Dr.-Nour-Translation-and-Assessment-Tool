# modules/student_interface.py
import streamlit as st
from modules.postedit_metrics import PostEditSession

def student_dashboard():
    st.subheader("Student Dashboard")

    original_text = st.text_area("Original Text (for post-editing)", "Translate this sentence...")
    translated_text = st.text_area("Your Translation")

    if st.button("Submit Translation"):
        session = PostEditSession(original_text, translated_text)
        st.write("**Edit Distance:**", session.edit_distance)
        st.write("**Edit Ratio:**", session.edit_ratio)
        st.write("**Errors:**", session.errors)
        st.success("Submission recorded!")
