import streamlit as st

st.set_page_config(page_title="Nour Translation & Assessment Tool", layout="wide")
st.title("Nour Translation & Assessment Tool")

# --- Modular Imports (Crash-Safe) ---
def safe_import(module_name, fallback):
    try:
        return __import__(module_name). __dict__
    except ModuleNotFoundError:
        st.warning(f"{module_name} not found. Feature disabled.")
        return fallback

# Import instructor
try:
    from instructor import instructor_dashboard
except:
    instructor_dashboard = lambda: st.info("Instructor dashboard unavailable.")

# Import student
try:
    from student_interface import student_dashboard
except:
    student_dashboard = lambda: st.info("Student dashboard unavailable.")

# Gamification
try:
    from gamification import leaderboard
except:
    leaderboard = lambda: None

# Postediting
try:
    from postediting import calculate_edit_distance, calculate_edit_ratio, highlight_errors, PostEditSession
except:
    calculate_edit_distance = calculate_edit_ratio = highlight_errors = PostEditSession = None

# Error analysis
try:
    from error_analysis import analyze_errors
except:
    analyze_errors = lambda s, t: []

# Time tracking
try:
    from time_tracking import track_session
except:
    track_session = lambda: None

# Suggestions
try:
    from suggestions import suggest_exercises
except:
    suggest_exercises = lambda history: []

# Badges
try:
    from badges import award_badges
except:
    award_badges = lambda score: []

# --- User Selection ---
user_type = st.radio("Login as:", ["Instructor", "Student"], index=1)

# --- Interface Display ---
if user_type == "Instructor":
    instructor_dashboard()
elif user_type == "Student":
    student_dashboard()

# --- Optional Leaderboard ---
leaderboard()
