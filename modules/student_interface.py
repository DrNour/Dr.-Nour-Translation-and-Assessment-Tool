import streamlit as st
import time

# Initialize storage
if "translations" not in st.session_state:
    st.session_state["translations"] = []
if "start_time" not in st.session_state:
    st.session_state["start_time"] = {}

def student_dashboard(exercise_id=1, source_text=None):
    st.title(f"Student Dashboard - Exercise {exercise_id}")

    # Default example text if none is passed
    if source_text is None:
        source_text = """Eight short texts (ranging from 200 to 300 words) 
        were chosen from opinion columns, news articles, and literary excerpts. 
        These texts were pre-tested for readability and lexical difficulty 
        to ensure they were comparable across tasks."""

    # Start timing for this exercise
    if exercise_id not in st.session_state["start_time"]:
        st.session_state["start_time"][exercise_id] = time.time()

    # Display source text
    st.subheader("Source Text (ST)")
    st.write(source_text)

    # Check if student already submitted something
    existing = next((t for t in st.session_state["translations"]
                     if t["exercise_id"] == exercise_id), None)

    # Input area for translation
    st.subheader("Your Translation")
    student_translation = st.text_area(
        "Write your translation here:",
        value=existing["translation"] if existing else "",
        height=200
    )

    # Save / update button
    if st.button("Save Translation"):
        if student_translation.strip():
            duration = time.time() - st.session_state["start_time"][exercise_id]
            keystrokes = len(student_translation)

            if existing:
                existing["translation"] = student_translation
                existing["time_spent_sec"] = round(duration, 2)
                existing["keystrokes"] = keystrokes
            else:
                st.session_state["translations"].append({
                    "exercise_id": exercise_id,
                    "source_text": source_text,
                    "translation": student_translation,
                    "time_spent_sec": round(duration, 2),
                    "keystrokes": keystrokes
                })

            st.success("✅ Your translation has been saved!")

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

    # Show all saved submissions
    if st.session_state["translations"]:
        st.subheader("📂 Your Saved Translations")
        for entry in st.session_state["translations"]:
            with st.expander(f"Exercise {entry['exercise_id']} - View Translation"):
                st.markdown(f"**Source Text:** {entry['source_text']}")
                st.markdown(f"**Your Translation:** {entry['translation']}")
                if "time_spent_sec" in entry:
                    st.markdown(f"⏱ Time Spent: {entry['time_spent_sec']} sec")
                    st.markdown(f"⌨️ Keystrokes: {entry['keystrokes']}")
