import streamlit as st
import pandas as pd

def instructor_dashboard():
    st.header("Instructor Dashboard")
    submissions = st.session_state.get("submissions", [])
    if submissions:
        df = pd.DataFrame(submissions)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download All Submissions",
            data=csv,
            file_name="submissions.csv",
            mime="text/csv"
        )
    else:
        st.info("No submissions yet.")
