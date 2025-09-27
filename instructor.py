import streamlit as st
import json
import os

EXERCISE_FILE = "data/exercises.json"
os.makedirs("data", exist_ok=True)

def load_exercises():
    if os.path.exists(EXERCISE_FILE):
        with open(EXERCISE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_exercises(exercises):
    with open(EXERCISE_FILE, "w", encoding="utf-8") as f:
        json.dump(exercises, f, ensure_ascii=False, indent=2)

def instructor_dashboard():
    st.header("Instructor Dashboard")

    exercises = load_exercises()

    # --- Create New Exercise ---
    with st.expander("➕ Create New Exercise"):
        title = st.text_input("Exercise Title")
        source_text = st.text_area("Source Text")
        reference = st.text_area("Reference Translation (optional)")

        if st.button("Save Exercise"):
            if title and source_text:
                new_ex = {
                    "title": title,
                    "source_text": source_text,
                    "reference": reference
                }
                exercises.append(new_ex)
                save_exercises(exercises)
                st.success(f"Exercise '{title}' saved!")
            else:
                st.error("Title and source text are required.")

    # --- Manage Exercises ---
    st.subheader("📂 Existing Exercises")
    if exercises:
        for i, ex in enumerate(exercises):
            st.markdown(f"**{ex['title']}**")
            st.text_area("Source", ex["source_text"], height=80, disabled=True)
            st.text_area("Reference", ex["reference"], height=80, disabled=True)

            if st.button(f"Delete {ex['title']}", key=f"delete_{i}"):
                exercises.pop(i)
                save_exercises(exercises)
                st.warning(f"Deleted exercise: {ex['title']}")
                st.rerun()
    else:
        st.info("No exercises found. Create one above.")
