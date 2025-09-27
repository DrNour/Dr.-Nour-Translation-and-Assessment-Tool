import streamlit as st
from modules.postedit_interface import postedit_dashboard

def student_dashboard():
    st.header("Student Dashboard")
    
    st.subheader("Translate From Scratch")
    translation = st.text_area("Enter your translation here")
    reference = st.text_area("Optional reference translation")
    if st.button("Submit Translation"):
        st.success("Translation submitted!")
    
    st.subheader("Post-edit MT Output")
    postedit_dashboard(student_name="CurrentStudent")
