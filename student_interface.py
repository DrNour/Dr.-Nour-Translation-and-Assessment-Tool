import streamlit as st
import os
import pandas as pd
from datetime import datetime

DATA_FILE = "submissions.csv"

def student_dashboard():
    st.subheader("Student Workspace")

    student_name = st.text_input("Enter your name")
    source_text = st.text_area("Source Text (ST)")
    target_translation = st.text_area("Your Translation (TT)")
    reference = st.text_area("Reference Translation (optional)")

    mode = st.radio("Mode:", ["Translate from Scratch", "Post-edit MT Output"])

    if st.button("Submit"):
        if not student_name or not target_translation:
            st.error("Name and translation are required.")
            return

        # create dataframe row
        new_entry = {
            "student": student_name,
            "mode": mode,
            "source": source_text,
            "translation": target_translation,
            "reference": reference,
            "timestamp": datetime.now().isoformat()
        }

        # append to file
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            df = pd.DataFrame([new_entry])

        df.to_csv(DATA_FILE, index=False)

        st.success("✅ Submission saved successfully!")
        st.balloons()
