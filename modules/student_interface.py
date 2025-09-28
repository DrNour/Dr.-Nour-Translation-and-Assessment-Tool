import streamlit as st
import time
import json
from modules.evaluation import evaluate_translation

# Initialize storage
if "translations" not in st.session_state:
    st.session_state["translations"] = []
if "start_time" not in st.session_state:
    st.session_state["start_time"] = {}

# Optional: load previous submissions from file
try:
    with open("submissions.json", "r") as f:
        st.session_state["translations"] = json.load(f)
except FileNotFoundError:
    pass

def save_to_file():
    """Persist submissions to JSON so they survive for days."""
    with open("submissions.json", "w") as f:
        json.dump(st.session_state["translations"], f, indent=2)

def student_dashboard():
    st.title("Student Dashboard")

    # Check assigned exercises
    if "exercises" not in st.session_state or not any(ex["assigned"] for ex in st.session_state["exercises"]):
        st.warning("⚠️ No exercises assigned yet.")
        return

    # Student info
    student_name = st.text_input("Enter Your Name:", key="student_name")
    if not student_name.strip():
        st.warning("Please enter your name before starting an exercise.")
        return

    for ex in [e for e in st.session_state["exercises"] if e["assigned"]]:
        exercise_id = ex["id"]
        source_text = ex["source_text"]

        st.subheader(f"Exercise {exercise_id}")
        st.markdown("**Source Text (ST):**")
        st.info(source_text)

        # Initialize start time for exercise
        if exercise_id not in st.session_state["start_time"]:
            st.session_state["start_time"][exercise_id] = time.time()

        # Check if student already submitted this exercise
        existing = next((t for t in st.session_state["translations"]
                         if t["exercise_id"] == exercise_id and t["student_name"] == student_name), None)

        # Translation input area
        student_translation = st.text_area(
            "Your Translation:",
            value=existing["translation"] if existing else "",
            height=150,
            key=f"trans_{exercise_id}_{student_name}"
        )

        # Save / update translation
        if st.button("Save Translation", key=f"save_{exercise_id}_{student_name}"):
            if student_translation.strip():
                duration = time.time() - st.session_state["start_time"][exercise_id]
                fluency, accuracy = evaluate_translation(source_text, student_translation)

                record = {
                    "exercise_id": exercise_id,
                    "student_name": student_name,
                    "source_text": source_text,
                    "translation": student_translation,
                    "time_spent_sec": round(duration, 2),
                    "keystrokes": len(student_translation),
                    "fluency": fluency,
                    "accuracy": accuracy
                }

                if existing:
                    # Update existing submission
                    st.session_state["translations"].remove(existing)
                st.session_state["translations"].append(record)
                save_to_file()  # Persist to JSON
                st.success("✅ Translation saved with metrics!")

        # Comparison view
        if student_translation.strip():
            st.subheader("Comparison View")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Source Text**")
                st.write(source_text)
            with col2:
                st.markdown("**Your Translation**")
                st.write(student_translation)

        # Show previous submissions for this exercise
        if existing:
            st.subheader("📊 Previous Submission Metrics")
            st.markdown(f"- **Fluency:** {existing['fluency']}")
            st.markdown(f"- **Accuracy:** {existing['accuracy']}")
            st.markdown(f"- **Time Spent:** {existing['time_spent_sec']} sec")
            st.markdown(f"- **Keystrokes:** {existing['keystrokes']}")
            st.markdown("---")
