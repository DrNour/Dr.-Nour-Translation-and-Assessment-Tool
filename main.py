# main.py
import streamlit as st
import time

st.set_page_config(page_title="Nour Translation & Assessment Tool", layout="wide")
st.title("Nour Translation & Assessment Tool")

# --- Crash-Safe Imports ---
try:
    from modules.postediting import calculate_edit_distance, calculate_edit_ratio, highlight_errors, PostEditSession
except ModuleNotFoundError:
    st.warning("Post-edit metrics module not found. Core evaluation may be limited.")
    calculate_edit_distance = calculate_edit_ratio = highlight_errors = PostEditSession = None

try:
    from modules.instructor import instructor_dashboard
except ModuleNotFoundError:
    st.warning("Instructor interface module not found. Instructor features disabled.")
    instructor_dashboard = lambda: st.info("Instructor dashboard unavailable.")

try:
    from modules.student_interface import student_dashboard
except ModuleNotFoundError:
    st.warning("Student interface module not found. Student features disabled.")
    student_dashboard = lambda: st.info("Student dashboard unavailable.")

try:
    from modules.badges import award_badge
except ModuleNotFoundError:
    st.warning("Badges module not found. Badge features disabled.")
    award_badge = lambda *args, **kwargs: None

# --- User Selection ---
user_type = st.radio("Login as:", ["Instructor", "Student"], index=1)

# --- Interface Display ---
if user_type == "Instructor":
    instructor_dashboard()
elif user_type == "Student":
    # Track start time for the student session
    start_time = time.time()
    student_dashboard()
    end_time = time.time()
    st.info(f"Time spent on exercises: {int(end_time - start_time)} seconds")

    # If post-edit metrics module is available, show summary
    if PostEditSession:
        st.header("Post-Edit Metrics Example")
        # Example placeholders, you can adapt to your exercises
        original_text = st.session_state.get("original_text", "")
        student_translation = st.session_state.get("student_translation", "")
        if original_text and student_translation:
            session = PostEditSession(original_text, student_translation)
            summary = session.summary()
            st.write(f"Edit Distance: {summary['edit_distance']}")
            st.write(f"Edit Ratio: {summary['edit_ratio']:.2f}")
            st.write("Errors Highlighted:")
            for err_type, orig_part, stud_part in summary["errors"]:
                st.write(f"{err_type} | Original: '{orig_part}' | Student: '{stud_part}'")

# --- Optional Leaderboard ---
leaderboard()

