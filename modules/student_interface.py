import streamlit as st
import time
from modules.evaluation import evaluate_translation  # your fluency/accuracy function

# Initialize storage
if "translations" not in st.session_state:
    st.session_state["translations"] = []
if "start_time" not in st.session_state:
    st.session_state["start_time"] = {}

def student_dashboard():
    st.title("Student Dashboard")

    # Check assigned exercises
    if "exercises" not in st.session_state or not any(ex["assigned"] for ex in st.session_state["exercises"]):
        st.warning("⚠️ No exercises assigned yet.")
        return

    for ex in [e for e in st.session_state["exercises"] if e["assigned"]]:
        exercise_id = ex["id"]
        source_text = ex["source_text"]

        st.subheader(f"Exercise {exercise_id}")
        st.markdown("**Source Text (ST):**")
        st.info(source_text)

        # Start timing for this exercise
        if exercise_id not in st.session_state["start_time"]:
            st.session_state["start_time"][exercise_id] = time.time()

        # Check if student already submitted
        existing = next((t for t in st.session_state["translations"]
                         if t["exercise_id"] == exercise_id), None)

        # Translation input area
        student_translation = st.text_area(
            "Your Translation:",
            value=existing["translation"] if existing else "",
            height=150,
            key=f"trans_{exercise_id}"
        )

        # Save / update translation
        if st.button("Save Translation", key=f"save_{exercise_id}"):
            if student_translation.strip():
                duration = time.time() - st.session_state["start_time"][exercise_id]
                fluency, accuracy = evaluate_translation(source_text, student_translation)

                if existing:
                    existing["translation"] = student_translation
                    existing["time_spent_sec"] = round(duration, 2)
                    existing["keystrokes"] = len(student_translation)
                    existing["fluency"] = fluency
                    existing["accuracy"] = accuracy
                else:
                    st.session_state["translations"].append({
                        "exercise_id": exercise_id,
                        "source_text": source_text,
                        "translation": student_translation,
                        "time_spent_sec": round(duration, 2),
                        "keystrokes": len(student_translation),
                        "fluency": fluency,
                        "accuracy": accuracy
                    })

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
