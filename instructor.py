import streamlit as st
import pandas as pd

def instructor_panel():
    st.header("Instructor Interface")
    new_exercise = st.text_area("Create a new translation exercise:")
    if st.button("Save Exercise"):
        # Save to CSV or DB
        st.success("Exercise saved!")
