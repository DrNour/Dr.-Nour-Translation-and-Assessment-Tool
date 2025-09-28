import streamlit as st
from modules.student_interface import student_dashboard
from modules.instructor import instructor_dashboard

st.title("Translation & Post-Editing Tool - Production Version")

tab = st.sidebar.selectbox("Select Dashboard", ["Student", "Instructor"])

if tab == "Student":
    student_dashboard()
else:
    instructor_dashboard()
