import streamlit as st
import pandas as pd
import os

DATA_FILE = "submissions.csv"

def instructor_dashboard():
    st.subheader("Instructor Dashboard")

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.dataframe(df)

        st.download_button(
            "Download Submissions CSV",
            df.to_csv(index=False).encode("utf-8"),
            "submissions.csv",
            "text/csv"
        )
    else:
        st.info("No student submissions yet.")
