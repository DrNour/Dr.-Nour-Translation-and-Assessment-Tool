import streamlit as st
from modules.postedit_metrics import PostEditSession, calculate_edit_distance, calculate_edit_ratio, highlight_errors
import time

def student_dashboard():
    st.header("Student Dashboard")
    st.info("Translate from scratch or post-edit MT output.")

    source_text = st.text_area("Source text to translate:")
    mt_output = st.text_area("Optional MT output (leave blank to translate from scratch):")

    session = PostEditSession()
    translation = st.text_area("Your Translation:", value=mt_output)

    if st.button("Submit Translation"):
        session.add_keystrokes(len(translation))
        elapsed = session.elapsed_time()
        edit_dist = calculate_edit_distance(mt_output, translation) if mt_output else 0
        edit_ratio = calculate_edit_ratio(mt_output, translation) if mt_output else 0
        errors = highlight_errors(mt_output, translation) if mt_output else []

        st.success("Translation submitted!")
        st.write(f"Time spent: {elapsed:.2f} seconds")
        st.write(f"Keystrokes: {session.keystrokes}")
        st.write(f"Edit distance: {edit_dist}")
        st.write(f"Edit ratio: {edit_ratio:.2f}")
        st.write(f"Highlighted differences: {errors}")
