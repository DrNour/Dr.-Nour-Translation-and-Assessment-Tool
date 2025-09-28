import streamlit as st
from modules.student_interface import student_dashboard
from modules.instructor import instructor_dashboard
import json

# Load exercises
with open("modules/exercises.json", "r", encoding="utf-8") as f:
    EXERCISES = json.load(f)

st.title("Translation & Post-Editing Tool - Multi-Exercise Version")

tab = st.sidebar.selectbox("Select Dashboard", ["Student", "Instructor"])

if tab == "Student":
    student_dashboard(EXERCISES)
else:
    instructor_dashboard(EXERCISES)   # <-- pass EXERCISES
