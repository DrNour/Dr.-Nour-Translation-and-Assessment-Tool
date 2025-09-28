import streamlit as st
import pandas as pd

def instructor_dashboard():
    st.header("Instructor Dashboard")
    st.info("Here you can create exercises, download submissions, and view metrics.")


    # ---------- Create Exercise ----------
    with st.form("create_exercise_form"):
        exercise_id = st.text_input("Exercise ID (unique)")
        source_text = st.text_area("Source Text (English)")
        target_text = st.text_area("Reference Translation (Arabic)")
        submit_exercise = st.form_submit_button("Create Exercise")

        if submit_exercise:
            if exercise_id in exercises:
                st.error("❌ Exercise ID already exists. Choose another one.")
            elif not source_text or not target_text:
                st.error("⚠️ Please provide both source text and reference translation.")
            else:
                exercises[exercise_id] = {
                    "source": source_text,
                    "reference": target_text,
                }
                st.success(f"✅ Exercise '{exercise_id}' created successfully!")

    # ---------- Show All Exercises ----------
    if exercises:
        st.subheader("📚 Existing Exercises")
        for ex_id, ex_data in exercises.items():
            with st.expander(f"Exercise {ex_id}"):
                st.write("**Source Text:**")
                st.write(ex_data["source"])
                st.write("**Reference Translation:**")
                st.write(ex_data["reference"])

    # ---------- Student Submissions ----------
    if submissions:
        st.subheader("📥 Student Submissions")

        all_data = []
        for ex_id, sub_data in submissions.items():
            st.markdown(f"### Exercise {ex_id}")
            for student, data in sub_data.items():
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

        # Download Submissions as CSV
        if all_data:
            df = pd.DataFrame(all_data)
            st.download_button(
                label="📥 Download Submissions as CSV",
                data=df.to_csv(index=False),
                file_name="submissions.csv",
                mime="text/csv",
            )




