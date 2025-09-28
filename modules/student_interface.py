import streamlit as st
from modules.postediting import PostEditSession

def student_dashboard(EXERCISES):
    st.header("Student Dashboard")

    student_name = st.text_input("Enter your name")

    exercise_options = [f"{ex['id']}: {ex['text'][:50]}..." for ex in EXERCISES]
    selected = st.selectbox("Select an exercise", exercise_options)

    # Map selection to exercise
    exercise_index = exercise_options.index(selected)
    exercise = EXERCISES[exercise_index]

    if st.button("Start Editing"):
        if not student_name.strip():
            st.error("Please enter your name!")
            return

        session = PostEditSession(exercise['text'], student_name, exercise['id'])
        session.start_edit()
        st.session_state.current_session = session
        st.session_state.editing = True
        st.experimental_rerun()

    if st.session_state.get("editing"):
        session: PostEditSession = st.session_state.current_session
        edited_text = st.text_area("Edit Text", session.original_text, key="edit_box")

        if st.button("Finish Editing"):
            session.finish_edit(edited_text)
            st.success(f"Submission saved! Metrics: {session.metrics}")

            # Save submission
            if "submissions" not in st.session_state:
                st.session_state.submissions = []
            st.session_state.submissions.append({
                "SubmissionID": session.id,
                "ExerciseID": session.exercise_id,
                "Student": session.student_name,
                "Original": session.original_text,
                "Edited": session.edited_text,
                **session.metrics
            })

            # Clear current session
            st.session_state.editing = False
            del st.session_state.current_session
            st.experimental_rerun()
