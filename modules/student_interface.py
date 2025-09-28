import streamlit as st
import time
from modules.evaluation import evaluate_translation  # your fluency/accuracy metrics

if "translations" not in st.session_state:
    st.session_state["translations"] = []
if "start_time" not in st.session_state:
    st.session_state["start_time"] = {}

def student_dashboard():
    st.title("Student Dashboard")

    if "exercises" not in st.session_state or not any(ex["assigned"] for ex in st.session_state["exercises"]):
        st.warning("⚠️ No exercises assigned yet.")
        return

    for ex in [e for e in st.session_state["exercises"] if e["assigned"]]:
        exercise_id = ex["id"]
        source_text = ex["source_text"]

        st.subheader(f"Exercise {exercise_id}")
        st.markdown("**Source Text (ST):**")
        st.info(source_text)

        if exercise_id not in st.session_state["start_time"]:
            st.session_state["start_time"][exercise_id] = time.time()

        # Check if student already submitted
        existing = next((t for t in st.session_state["translations"]
                         if t["exercise_id"] == exercise_id), None)

        student_translation = st.text_area(
            "Your Translation:",
            value=existing["translation"] if existing else "",
            height=150,
            key=f"trans_{exercise_id}"
        )

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

                st.success("✅ Translation saved with assessment!")

        if existing:
            st.markdown(f"**Fluency Score:** {existing['fluency']}")
            st.markdown(f"**Accuracy Score:** {existing['accuracy']}")
            st.markdown(f"⏱ Time Spent: {existing['time_spent_sec']} sec")
            st.markdown(f"⌨️ Keystrokes: {existing['keystrokes']}")
            st.markdown("---")
