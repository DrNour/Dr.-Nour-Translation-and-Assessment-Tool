import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

import streamlit as st
import student_interface
import instructor_interface

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["Student", "Instructor"])

if choice == "Student":
    student_interface.student_dashboard()
else:
    instructor_interface.instructor_dashboard()
