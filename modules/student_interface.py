import streamlit as st
from modules.postediting import PostEditSession

def student_dashboard():
    st.header("Student Dashboard")

    # Initialize session_state keys
    if "exercises" not in st.session_state:
        st.session_state.exercises = []
    if "assignments" not in st.session_state:
        st.session_state.assignments = {}
    if "submissions" not in st.session_state:
        st.session_state.submissions = []
    if "editing" not in st.session_state:
        st.session_state.editing = False
    if "current_session" not in st.session_state:
        st.session_state.current_session = None

    # Student info
    student_name = st.text_input("Enter your name")

    # Access mode
    access_mode = st.radio(
        "Select Access Mode",
        ["Assigned Exercises Only", "Open Exercises"]
    )

    # Determine exercises to show
    if access_mode == "Assigned Exercises Only":
        assigned_ids = st.session_state.assignments.get(student_name, [])
        exercises_to_show = [ex for ex in st.session_state.exercises if ex['id'] in assigned_ids]
        if not student_name.strip():
            st.warning("Please enter your name to see assigned exercises.")
            return
        elif not exercises_to_show:
            st.info("No exercises assigned yet. Ask your instructor.")
            return
    else:
        exercises_to_show = st.session_state.exercises
        if not exercises_to_show:
            st.info("No exercises available yet.")
            return

    # Select exercise
    exercise_options = [f"{ex['id']}: {ex['text'][:50]}..." for ex in exercises_to_show]
    selected = st.selectbox("Select an exercise", exercise_options)
    exercise_index = exercise_options.index(selected)
    exercise = exercises_to_show[exercise_index]

    # Start editing
    if st.button("Start Editing") and not st.session_state.editing:
        if not student_name.strip():
            st.warning("Please enter your name!")
        else:
            session = PostEditSession(exercise['text'], student_name, exercise['id'])
            session.start_edit()
            st.session_state.current_session = session
            st.session_state.editing = True

    # Editing area
    if st.session_state.editing and st.session_state.current_session:
        session: PostEditSession = st.session_state.current_session
        edited_text = st.text_area(
            "Edit Text",
            value=session.original_text,
            key=f"edit_box_{session.exercise_id}"
        )

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

            # Reset session
            st.session_state.editing = False
            st.session_state.current_session = None
