import streamlit as st
from modules import student_interface, instructor_interface

st.title("Translation & Post-Editing Tool - Production Version")

tab = st.sidebar.selectbox("Select Dashboard", ["Student", "Instructor"])

if tab == "Student":
    student_dashboard()
else:
    instructor_dashboard()

