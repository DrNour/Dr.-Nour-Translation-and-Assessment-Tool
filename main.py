# main.py
import streamlit as st
from postedit_metrics import calculate_edit_distance, calculate_edit_ratio, highlight_errors, PostEditSession

st.set_page_config(page_title="Translation Evaluation Tool", layout="wide")
st.title("Dr. Nour Translation & Post-Editing Assessment Tool")

# Student submission interface
st.header("Student Translation Submission")
source_text = st.text_area("Source Text", height=100)
student_translation = st.text_area("Your Translation / Post-Edit", height=100)
optional_reference = st.text_area("Optional Reference Translation", height=100)

# Post-editing session tracker
session = PostEditSession()
if st.button("Start Editing"):
    session.start()
    st.success("Editing session started! Time is being tracked.")

if st.button("Finish Editing"):
    session.end()
    session.add_keystrokes(len(student_translation))
    st.success(f"Editing session finished! Duration: {session.get_duration()} sec, Keystrokes: {session.keystrokes}")

# Evaluate translations
if st.button("Evaluate Translation"):
    if source_text and student_translation:
        distance = calculate_edit_distance(source_text, student_translation)
        ratio = calculate_edit_ratio(source_text, student_translation)
        errors = highlight_errors(source_text, student_translation)

        st.subheader("Post-Editing Metrics")
        st.write(f"Edit Distance: {distance}")
        st.write(f"Normalized Edit Distance: {ratio:.2f}")
        st.write("Detected Errors (positions & type):")
        st.write(errors)

        st.subheader("Session Summary")
        st.write(session.summary())
    else:
        st.warning("Please enter both source text and your translation.")
