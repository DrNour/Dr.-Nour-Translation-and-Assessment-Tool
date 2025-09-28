import streamlit as st
import json
import time
from pathlib import Path
from modules.postediting import calculate_edit_distance, calculate_edit_ratio
from modules.gamification import update_leaderboard, show_leaderboard, award_badges

EXERCISE_FILE = Path(__file__).parent / "exercises.json"

def load_exercises():
    if EXERCISE_FILE.exists():
        with open(EXERCISE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def student_dashboard():
    st.header("Student Dashboard")

    student_name = st.text_input("Enter your name")
    if not student_name:
        st.info("Please enter your name to continue.")
        return

    exercises = load_exercises()
    if not exercises:
        st.info("No exercises available. Please wait for instructor to create some.")
        return

    from modules.postediting import calculate_edit_distance, calculate_edit_ratio, highlight_errors

def student_interface(exercises, submissions):
    st.header("Student Dashboard")

    # Student name
    student_name = st.text_input("Enter your name")
    if not student_name:
        st.warning("Please enter your name to continue.")
        return

    # Pick exercise
    if not exercises:
        st.info("No exercises available yet.")
        return

    exercise_id = st.selectbox("Select Exercise", list(exercises.keys()))
    exercise = exercises[exercise_id]

    st.write("**Source Text:**")
    st.write(exercise["source"])

    # Student translation
    student_translation = st.text_area("Your Translation")

    # Timer (for time spent)
    import time
    if "start_time" not in st.session_state:
        st.session_state["start_time"] = time.time()

    if st.button("Submit Translation"):
        if not student_translation.strip():
            st.warning("Please enter a translation before submitting.")
        else:
            elapsed_time = int(time.time() - st.session_state["start_time"])

            # Metrics
            distance = calculate_edit_distance(exercise["reference"], student_translation)
            ratio = calculate_edit_ratio(exercise["reference"], student_translation)
            st.write(f"**Edit Distance:** {distance}")
            st.write(f"**Edit Ratio:** {ratio:.2f}")

            # Error highlighting
            st.markdown("**Error Analysis:**")
            st.write(highlight_errors(exercise["reference"], student_translation), unsafe_allow_html=True)

            # Save submission
            if exercise_id not in submissions:
                submissions[exercise_id] = {}
            submissions[exercise_id][student_name] = {
                "translation": student_translation,
                "postedit": "",
                "time": elapsed_time,
            }

            st.success("✅ Translation submitted successfully!")


    exercise = st.selectbox(
        "Select Exercise",
        exercises,
        format_func=lambda x: x["text"][:50]+"..." if len(x["text"]) > 50 else x["text"]
    )
    original_text = exercise.get("text", "")
    reference_translation = exercise.get("reference", "")

    # Timer start
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    student_translation = st.text_area("Your Translation")

    if st.button("Submit Translation"):
        if not student_translation.strip():
            st.warning("Please enter a translation before submitting.")
        else:
            end_time = time.time()
            time_spent = int(end_time - st.session_state.start_time)

            distance = calculate_edit_distance(original_text, student_translation)
            ratio = calculate_edit_ratio(original_text, student_translation)

            # Calculate score
            score = max(0, 100 - (distance * 2 + time_spent / 2))

            st.success("Translation submitted successfully!")
            st.write(f"⏱ Time Spent: {time_spent} seconds")
            st.write(f"✏️ Edit Distance: {distance}")
            st.write(f"📊 Edit Ratio: {ratio:.2f}")
            st.write(f"🏆 Score: {score:.2f}")

            # Award badges
            badges = award_badges(student_name, score, ratio, time_spent)
            if badges:
                st.write("🎖️ Badges earned: " + ", ".join(badges))

            # Update leaderboard
            update_leaderboard(student_name, score)

            # Reset timer
            st.session_state.start_time = time.time()

    st.subheader("Leaderboard")
    show_leaderboard()

