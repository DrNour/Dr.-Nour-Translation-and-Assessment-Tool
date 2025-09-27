import streamlit as st
import time

st.set_page_config(page_title="Nour Translation & Assessment Tool", layout="wide")
st.title("Nour Translation & Assessment Tool")

# --- Modular Imports (Crash-Safe) ---
try:
    from modules.postediting import calculate_edit_distance, calculate_edit_ratio, highlight_errors, PostEditSession
except ModuleNotFoundError:
    st.warning("Post-edit metrics module not found. Core evaluation may be limited.")
from modules.postediting import calculate_edit_distance, calculate_edit_ratio, highlight_errors, PostEditSession

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
    from modules.gamification import leaderboard
except ModuleNotFoundError:
    st.warning("Gamification module not found. Leaderboard features disabled.")
    leaderboard = lambda: None

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
    student_dashboard()

# --- Optional Leaderboard ---
leaderboard()

