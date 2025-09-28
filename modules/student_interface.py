import streamlit as st
import time
from modules.postediting import calculate_edit_distance, calculate_edit_ratio, highlight_errors

def student_dashboard(exercises, submissions):
    st.header("Student Dashboard")

    # --- Student name ---
    student_name = st.text_input("Enter your name")
    if not student_name:
        st.warning("Please enter your name to continue.")
        return

    # --- Show available exercises ---
    if not exercises:
        st.info("No exercises available yet. Please wait for your instructor.")
        return

    exercise_id = st.selectbox("Select Exercise", list(exercises.keys()))
    exercise = exercises[exercise_id]

    st.subheader("Source Text")
    st.write(exercise["source"])

    # --- Student translation box ---
    student_translation = st.text_area("Your Translation")

    # --- Timer tracking ---
    if "start_time" not in st.session_state:
        st.session_state["start_time"] = time.time()

    # --- Submit translation ---
    if st.button("Submit Translation"):
        if not student_translation.strip():
            st.warning("Please enter a translation before submitting.")
        else:
            elapsed_time = int(time.time() - st.session_state["start_time"])

            # Calculate post-editing metrics
            reference = exercise.get("reference", "")
            distance = calculate_edit_distance(reference, student_translation)
            ratio = calculate_edit_ratio(reference, student_translation)

            st.markdown("### 📊 Post-Editing Metrics")
            st.write(f"**Edit Distance:** {distance}")
            st.write(f"**Edit Ratio:** {ratio:.2f}")

            # Error highlighting
            st.markdown("### 📝 Error Analysis")
            st.write(highlight_errors(reference, student_translation), unsafe_allow_html=True)

            # Save submission
            if exercise_id not in submissions:
                submissions[exercise_id] = {}
            submissions[exercise_id][student_name] = {
                "translation": student_translation,
                "postedit": "",
                "time": elapsed_time,
                "distance": distance,
                "ratio": ratio,
            }

            st.success("✅ Translation submitted successfully!")
