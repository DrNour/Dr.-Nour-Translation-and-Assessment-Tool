import streamlit as st
from modules import student_interface, instructor_interface

def main():
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Student", "Instructor"])

    if choice == "Student":
        student_interface.student_dashboard()
    elif choice == "Instructor":
        instructor_interface.instructor_dashboard()

if __name__ == "__main__":
    main()
