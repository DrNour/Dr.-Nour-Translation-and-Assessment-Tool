import streamlit as st
import time

st.set_page_config(page_title="Nour Translation & Assessment Tool", layout="wide")
st.title("Nour Translation & Assessment Tool")

# --- Core Modules (Crash-Safe) ---
try:
    from modules.postediting import calculate_edit_distance, calculate_edit_ratio, highlight_errors, PostEditSession
except Exception as e:
    st.warning(f"Post-edit metrics unavailable: {e}")
    calculate_edit_distance = calculate_edit_ratio = highlight_errors = PostEditSession = None

try:
    from modules.instructor import instructor_dashboard
except Exception as e:
    st.warning(f"Instructor interface unavailable: {e}")
    instructor_dashboard = lambda: st.info("Instructor dashboard unavailable.")

try:
    from modules.student_interface import student_dashboard
except Exception as e:
    st.warning(f"Student interface unavailable: {e}")
    student_dashboard = lambda: st.info("Student dashboard unavailable.")

# Optional modules (won't crash if missing)
try:
    from modules.badges import award_badge
except Exception as e:
    st.warning(f"Badges unavailable: {e}")
    award_badge = lambda *args, **kwargs: None

try:
    # Commented out until fixed to avoid crash
    # from modules.gamification import leaderboard
    leaderboard = lambda: None
except Exception as e:
    st.warning(f"Gamification unavailable: {e}")
    leaderboard = lambda: None

try:
    from modules.evaluation import bleu_metric, chrf_metric, bert_metric
except Exception as e:
    st.warning(f"Evaluation metrics unavailable: {e}")
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
