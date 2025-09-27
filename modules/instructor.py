import streamlit as st

def instructor_dashboard():
    st.header("Instructor Dashboard")
    st.info("Create exercises and view student submissions here.")

    with st.expander("Create a New Exercise"):
        exercise_text = st.text_area("Enter source text for translation:")
        if st.button("Create Exercise"):
            st.success("Exercise created! (This is a placeholder, data persistence not implemented.)")

    with st.expander("View Submissions"):
        st.info("Student submissions will appear here (placeholder).")
