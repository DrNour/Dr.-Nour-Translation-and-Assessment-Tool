import time
import streamlit as st

def track_session():
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    if st.button("End Session"):
        end_time = time.time()
        duration = end_time - st.session_state.start_time
        st.success(f"⏱ Time spent: {duration:.2f} seconds")
