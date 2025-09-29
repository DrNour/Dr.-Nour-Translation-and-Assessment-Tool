import streamlit as st
import importlib.util
import os

# Function to import a module from file
def import_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

BASE_DIR = os.path.dirname(__file__)
STUDENT_MODULE = import_module_from_path("student_interface", os.path.join(BASE_DIR, "modules", "student_interface.py"))
INSTRUCTOR_MODULE = import_module_from_path("instructor_interface", os.path.join(BASE_DIR, "modules", "instructor_interface.py"))

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["Student", "Instructor"])

if choice == "Student":
    STUDENT_MODULE.student_dashboard()
else:
    INSTRUCTOR_MODULE.instructor_dashboard()
