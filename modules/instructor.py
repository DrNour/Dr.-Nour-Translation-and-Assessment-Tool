import streamlit as st
import pandas as pd

def instructor_dashboard(EXERCISES):
    st.header("Instructor Dashboard")

    # Initialize session_state
    if "submissions" not in st.session_state:
        st.session_state.submissions = []
    if "assignments" not in st.session_state:
        st.session_state.assignments = {}  # {student_name: [exercise_ids]}

    # --- Assign exercises ---
    st.subheader("Assign Exercises to Students")
    student_name = st.text_input("Student Name to Assign Exercise")
    exercise_options = [f"{ex['id']}: {ex['text'][:50]}..." for ex in EXERCISES]
    selected_ex = st.multiselect("Select Exercises", exercise_options)

    if st.button("Assign"):
        if not student_name.strip() or not selected_ex:
            st.warning("Enter a student name and select at least one exercise")
        else:
            assigned_ids = [ex.split(":")[0] for ex in selected_ex]
            st.session_state.assignments[student_name] = assigned_ids
            st.success(f"Assigned {len(assigned_ids)} exercise(s) to {student_name}")

    # --- View current assignments ---
    if st.session_state.assignments:
        st.subheader("Current Assignments")
        for student, ex_list in st.session_state.assignments.items():
            st.write(f"{student}: {', '.join(ex_list)}")

    # --- View submissions and download ---
    if st.session_state.submissions:
        st.subheader("All Submissions")
        df = pd.DataFrame(st.session_state.submissions)
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
