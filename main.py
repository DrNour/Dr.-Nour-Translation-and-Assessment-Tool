import streamlit as st
import time

st.set_page_config(page_title="Nour Translation & Assessment Tool", layout="wide")
st.title("Nour Translation & Assessment Tool")

# --- Crash-Safe Imports ---
try:
    from modules.postediting import calculate_edit_distance, calculate_edit_ratio, highlight_errors, PostEditSession
except Exception as e:
    st.warning(f"Post-edit metrics module not found or failed: {e}")
    calculate_edit_distance = calculate_edit_ratio = highlight_errors = PostEditSession = None

try:
    from modules.instructor import instructor_dashboard
except Exception as e:
    st.warning(f"Instructor interface module not found or failed: {e}")
    instructor_dashboard = lambda: st.info("Instructor dashboard unavailable.")

try:
    from modules.student_interface import student_dashboard
except Exception as e:
    st.warning(f"Student interface module not found or failed: {e}")
    student_dashboard = lambda: st.info("Student dashboard unavailable.")

try:
    from modules.gamification import leaderboard
except Exception as e:
    st.warning(f"Gamification module not found or failed: {e}")
    leaderboard = lambda: None

try:
    from modules.badges import award_badge
except Exception as e:
    st.warning(f"Badges module not found or failed: {e}")
    award_badge = lambda *args, **kwargs: None

try:
    from modules.evaluation import bleu_metric, chrf_metric, bert_metric
except Exception as e:
    st.warning(f"Evaluation metrics module not found or failed: {e}")
    bleu_metric = chrf_metric = bert_metric = lambda *args, **kwargs: None

# --- User Selection ---
user_type = st.radio("Login as:", ["Instructor", "Student"], index=1)

# --- Interface Display ---
if user_type == "Instructor":
    instructor_dashboard()
elif user_type == "Student":
    student_dashboard()

# --- Optional Leaderboard ---
leaderboard()
