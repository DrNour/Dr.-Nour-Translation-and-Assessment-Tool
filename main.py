import streamlit as st
import time
import pandas as pd

# ----------------- SESSION STATE INIT -----------------
if "exercises" not in st.session_state:
    st.session_state["exercises"] = {}

if "submissions" not in st.session_state:
    st.session_state["submissions"] = {}

if "start_time" not in st.session_state:
    st.session_state["start_time"] = None


# ----------------- INSTRUCTOR INTERFACE -----------------
def instructor_interface():
    st.header("Instructor Dashboard")

    # Form to create new exercise
    with st.form("create_exercise_form"):
        exercise_id = st.text_input("Exercise ID (unique)")
        source_text = st.text_area("Source Text (English)")
        target_text = st.text_area("Reference Translation (Arabic)")
        submit_exercise = st.form_submit_button("Create Exercise")

        if submit_exercise:
            if exercise_id in st.session_state["exercises"]:
                st.error("❌ Exercise ID already exists. Choose another one.")
            elif not source_text or not target_text:
                st.error("⚠️ Please provide both source text and reference translation.")
            else:
                st.session_state["exercises"][exercise_id] = {
                    "source": source_text,
                    "reference": target_text,
                }
                st.success(f"✅ Exercise '{exercise_id}' created successfully!")

    # Show all created exercises
    if st.session_state["exercises"]:
        st.subheader("📚 Existing Exercises")
        for ex_id, ex_data in st.session_state["exercises"].items():
            with st.expander(f"Exercise {ex_id}"):
                st.write("**Source Text:**")
                st.write(ex_data["source"])
                st.write("**Reference Translation:**")
                st.write(ex_data["reference"])

    # Student Submissions
    if st.session_state["submissions"]:
        st.subheader("📥 Student Submissions")

        all_data = []
        for ex_id, submissions in st.session_state["submissions"].items():
            st.markdown(f"### Exercise {ex_id}")
            for student, data in submissions.items():
                st.markdown(f"**👤 {student}**")
                st.write("**Student Translation:**", data["translation"])
                st.write("**Post-Edited Translation:**", data["postedit"])
                st.write("**Time Spent (seconds):**", data["time"])
                st.write("---")
                all_data.append(
                    {
                        "Exercise": ex_id,
                        "Student": student,
                        "Translation": data["translation"],
                        "Post-Edited": data["postedit"],
                        "Time Spent (s)": data["time"],
                    }
                )

        # Export submissions as CSV
        if all_data:
            df = pd.DataFrame(all_data)
            st.download_button(
                label="📥 Download Submissions as CSV",
                data=df.to_csv(index=False),
                file_name="submissions.csv",
                mime="text/csv",
            )


# ----------------- STUDENT INTERFACE -----------------
def student_interface():
    st.header("Student Workspace")

    student_name = st.text_input("Enter your name:")

    if not student_name:
        st.warning("⚠️ Please enter your name to continue.")
        return

    if not st.session_state["exercises"]:
        st.info("No exercises available yet. Please wait for the instructor to create one.")
        return

    # Select an exercise
    exercise_id = st.selectbox("Choose an exercise:", list(st.session_state["exercises"].keys()))

    exercise = st.session_state["exercises"][exercise_id]
    st.write("### Source Text")
    st.write(exercise["source"])

    # Start timer
    if st.session_state["start_time"] is None:
        st.session_state["start_time"] = time.time()

    translation = st.text_area("Your Translation (Arabic):")
    postedit = st.text_area("Post-Edited Translation (Arabic):")

    if st.button("Submit Translation"):
        end_time = time.time()
        time_spent = int(end_time - st.session_state["start_time"])

        if exercise_id not in st.session_state["submissions"]:
            st.session_state["submissions"][exercise_id] = {}

        st.session_state["submissions"][exercise_id][student_name] = {
            "translation": translation,
            "postedit": postedit,
            "time": time_spent,
        }

        st.success("✅ Translation submitted successfully!")
        st.session_state["start_time"] = None  # reset timer


# ----------------- MAIN APP -----------------
def main():
    st.sidebar.title("Navigation")
    role = st.sidebar.radio("Login as:", ["Instructor", "Student"])

    if role == "Instructor":
        instructor_interface()
    else:
        student_interface()


if __name__ == "__main__":
    main()
