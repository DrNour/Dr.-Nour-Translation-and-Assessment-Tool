import streamlit as st

st.set_page_config(page_title="Nour Translation & Assessment Tool", layout="wide")
st.title("Nour Translation & Assessment Tool")

# --- Crash-safe imports ---
try:
    from modules.postediting import *
except ModuleNotFoundError:
    st.warning("Post-edit metrics module not found. Core evaluation may be limited.")

try:
    from modules.instructor import instructor_dashboard
except ModuleNotFoundError:
    st.warning("Instructor interface module not found.")
    instructor_dashboard = lambda: st.info("Instructor dashboard unavailable.")

try:
    from modules.student_interface import student_dashboard
except ModuleNotFoundError:
    st.warning("Student interface module not found.")
    student_dashboard = lambda: st.info("Student dashboard unavailable.")

try:
    from modules.gamification import leaderboard
except ModuleNotFoundError:
    st.warning("Gamification module not found.")
    leaderboard = lambda: None

# --- User Selection ---
user_type = st.radio("Login as:", ["Instructor", "Student"], index=1)

# --- Interface Display ---
if user_type == "Instructor":
    instructor_dashboard()
else:
    student_dashboard()

# --- Leaderboard ---
leaderboard()
