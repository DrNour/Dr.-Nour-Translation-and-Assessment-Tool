import streamlit as st
from modules.postediting import PostEditSession, calculate_edit_distance, calculate_edit_ratio
from modules.evaluation import bleu_metric, chrf_metric, bert_metric
from modules.error_analysis import categorize_errors
from modules.suggestions import suggest_exercises
from modules.instructor import instructor_dashboard
from modules.student_interface import student_dashboard
from modules.gamification import leaderboard

st.set_page_config(page_title="Nour Translation & Assessment Tool", layout="wide")
st.title("Nour Translation & Assessment Tool")

# User login
user_type = st.radio("Login as:", ["Instructor", "Student"], index=1)

if user_type == "Instructor":
    instructor_dashboard()
elif user_type == "Student":
    student_dashboard()
    
leaderboard()
