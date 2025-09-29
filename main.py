import streamlit as st
from modules import student_interface, instructor_interface

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["Student", "Instructor"])

if choice == "Student":
    student_interface.student_dashboard()
else:
    instructor_interface.instructor_dashboard()
