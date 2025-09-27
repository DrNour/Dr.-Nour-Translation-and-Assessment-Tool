import streamlit as st

# --- In-memory storage ---
exercises = {}
submissions = {}

def instructor_dashboard():
    st.subheader("Instructor Dashboard")
    menu = st.radio("Menu", ["Create Exercise", "View Submissions"])

    if menu == "Create Exercise":
        exercise_id = st.text_input("Exercise ID")
        text = st.text_area("Source Text")
        if st.button("Create Exercise"):
            if exercise_id and text:
                exercises[exercise_id] = text
                st.success(f"Exercise '{exercise_id}' created!")
            else:
                st.warning("Please provide ID and text.")

    elif menu == "View Submissions":
        exercise_id = st.selectbox("Select Exercise", list(submissions.keys()) or ["None"])
        if exercise_id != "None":
            for student, data in submissions[exercise_id].items():
                st.write(f"Student: {student}")
                st.write(f"Translation: {data['translation']}")
                st.write(f"Post-edit: {data.get('postedit', '')}")
                st.write(f"Time spent: {data.get('time', '')} seconds")
