import streamlit as st
from modules.postediting import PostEditSession, calculate_edit_distance, calculate_edit_ratio, highlight_errors
from modules.instructor import exercises, submissions
from modules.gamification import award_points

def student_dashboard():
    st.subheader("Student Dashboard")
    student_name = st.text_input("Your Name")
    exercise_id = st.selectbox("Select Exercise", list(exercises.keys()) or ["None"])
    original_text = exercises.get(exercise_id, "")

    if exercise_id != "None":
        mode = st.radio("Mode", ["Translate from scratch", "Post-edit MT output"])
        if mode == "Post-edit MT output":
            mt_output = st.text_area("MT Output", value=original_text[::-1])  # dummy MT output
        else:
            mt_output = ""

        student_translation = st.text_area("Your Translation")
        session = PostEditSession()
        session.start()

        if st.button("Submit Translation"):
            session.end()
            session.add_keystrokes(len(student_translation))
            distance = calculate_edit_distance(original_text, student_translation)
            ratio = calculate_edit_ratio(original_text, student_translation)
            errors = highlight_errors(original_text, student_translation)

            # Save submission
            if exercise_id not in submissions:
                submissions[exercise_id] = {}
            submissions[exercise_id][student_name] = {
                "translation": student_translation,
                "postedit": mt_output,
                "time": session.time_spent(),
                "keystrokes": session.keystrokes,
                "edit_distance": distance,
                "edit_ratio": ratio,
                "errors": errors
            }

            st.success(f"Translation submitted! Edit distance: {distance}, Edit ratio: {ratio}")
            award_points(student_name, 10)
