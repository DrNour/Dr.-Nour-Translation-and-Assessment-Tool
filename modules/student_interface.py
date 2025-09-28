import streamlit as st
from modules.postediting import PostEditSession

def student_dashboard(EXERCISES):
    st.header("Student Dashboard")

    # --- Initialize session_state keys safely ---
    if "editing" not in st.session_state:
        st.session_state.editing = False
    if "current_session" not in st.session_state:
        st.session_state.current_session = None
    if "submissions" not in st.session_state:
        st.session_state.submissions = []

    # --- Student name input ---
    student_name = st.text_input("Enter your name")

    # --- Exercise selection ---
    exercise_options = [f"{ex['id']}: {ex['text'][:50]}..." for ex in EXERCISES]
    selected = st.selectbox("Select an exercise", exercise_options)

    exercise_index = exercise_options.index(selected)
    exercise = EXERCISES[exercise_index]

    # --- Start editing ---
    if st.button("Start Editing") and not st.session_state.editing:
        if not student_name.strip():
            st.warning("Please enter your name before starting.")
        else:
            session = PostEditSession(exercise['text'], student_name, exercise['id'])
            session.start_edit()
            st.session_state.current_session = session
            st.session_state.editing = True

    # --- Editing area ---
    if st.session_state.editing and st.session_state.current_session:
        session: PostEditSession = st.session_state.current_session
        edited_text = st.text_area(
            "Edit Text", 
            value=session.original_text, 
            key=f"edit_box_{session.exercise_id}"
        )

        # --- Finish editing ---
        if st.button("Finish Editing"):
            session.finish_edit(edited_text)
            st.success(f"Submission saved! Metrics: {session.metrics}")

            # Save submission
            st.session_state.submissions.append({
                "SubmissionID": session.id,
                "ExerciseID": session.exercise_id,
                "Student": session.student_name,
                "Original": session.original_text,
                "Edited": session.edited_text,
                **session.metrics
            })

            # Reset editing session
            st.session_state.editing = False
            st.session_state.current_session = None
