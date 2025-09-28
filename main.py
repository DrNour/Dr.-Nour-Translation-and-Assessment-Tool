import streamlit as st
import pandas as pd

def instructor_dashboard():
    st.header("Instructor Dashboard")

    # Initialize session_state keys
    if "exercises" not in st.session_state:
        st.session_state.exercises = []
    if "assignments" not in st.session_state:
        st.session_state.assignments = {}
    if "submissions" not in st.session_state:
        st.session_state.submissions = []

    # --- Add new exercises ---
    st.subheader("Add New Exercise")
    new_text = st.text_area("Exercise Text", "")
    if st.button("Add Exercise"):
        if not new_text.strip():
            st.warning("Exercise text cannot be empty")
        else:
            new_id = f"EX{len(st.session_state.exercises)+1:03d}"
            st.session_state.exercises.append({"id": new_id, "text": new_text})
            st.success(f"Exercise {new_id} added!")

    # --- Assign exercises ---
    st.subheader("Assign Exercises to Students")
    student_name = st.text_input("Student Name to Assign Exercise", key="assign_student")
    exercise_options = [f"{ex['id']}: {ex['text'][:50]}..." for ex in st.session_state.exercises]
    selected_ex = st.multiselect("Select Exercises", exercise_options, key="assign_select")

    if st.button("Assign Exercises"):
        if not student_name.strip() or not selected_ex:
            st.warning("Enter a student name and select at least one exercise")
        else:
            assigned_ids = [ex.split(":")[0] for ex in selected_ex]
            st.session_state.assignments[student_name] = assigned_ids
            st.success(f"Assigned {len(assigned_ids)} exercise(s) to {student_name}")

    # --- View assignments ---
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
