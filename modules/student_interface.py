# modules/student_interface.py
import streamlit as st
import json
from pathlib import Path

EXERCISE_FILE = Path(__file__).parent / "exercises.json"

try:
    from modules.postediting import calculate_edit_distance, calculate_edit_ratio, PostEditSession
except ModuleNotFoundError:
    calculate_edit_distance = calculate_edit_ratio = PostEditSession = None

try:
    import sacrebleu
except ModuleNotFoundError:
    sacrebleu = None

try:
    from bert_score import score as bert_score
except ModuleNotFoundError:
    bert_score = None

def load_exercises():
    if EXERCISE_FILE.exists():
        with open(EXERCISE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def student_dashboard():
    st.header("Student Dashboard")

    exercises = load_exercises()
    if not exercises:
        st.info("No exercises available. Please wait for instructor to create some.")
        return

    exercise = st.selectbox(
        "Select Exercise",
        exercises,
        format_func=lambda x: x["text"][:50] + "..." if len(x["text"]) > 50 else x["text"]
    )
    original_text = exercise.get("text", "")
    reference_translation = exercise.get("reference", "")

    session = PostEditSession(original_text) if PostEditSession else None

    student_translation = st.text_area("Your Translation")

    if st.button("Submit Translation"):
        if not student_translation.strip():
            st.warning("Please enter a translation before submitting.")
            return

        st.success("Translation submitted successfully!")

        # Time spent
        if session:
            time_sec = session.finish()
            st.write(f"Time spent: {time_sec:.2f} seconds")

        # Post-edit metrics
        if calculate_edit_distance:
            distance = calculate_edit_distance(original_text, student_translation)
            ratio = calculate_edit_ratio(original_text, student_translation)
            st.write(f"Edit Distance: {distance}")
            st.write(f"Edit Ratio: {ratio:.2f}")

        # BLEU and chrF
        if sacrebleu and reference_translation:
            bleu = sacrebleu.corpus_bleu([student_translation], [[reference_translation]])
            chrf = sacrebleu.corpus_chrf([student_translation], [[reference_translation]])
            st.write(f"BLEU: {bleu.score:.2f}")
            st.write(f"chrF: {chrf.score:.2f}")

        # BERTScore
        if bert_score and reference_translation:
            P, R, F1 = bert_score([student_translation], [reference_translation], lang="en", rescale_with_baseline=True)
            st.write(f"BERTScore F1: {F1.mean().item():.2f}")
