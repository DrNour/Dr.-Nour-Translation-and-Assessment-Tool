import streamlit as st
import difflib
import time
import pandas as pd
import io
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.chrf_score import sentence_chrf
from docx import Document
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
import torch

# =========================
# APP CONFIG
# =========================
st.set_page_config(page_title="Translation Training Tool", layout="wide")
st.title("🎯 Translation Post-Editing & Evaluation Platform")

# =========================
# SESSION STATES
# =========================
if 'submissions' not in st.session_state:
    st.session_state['submissions'] = {}
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'student_translation' not in st.session_state:
    st.session_state['student_translation'] = ""

# =========================
# LOGIN SYSTEM
# =========================
role = st.radio("Select Role:", ["Student", "Instructor"])

if role == "Instructor":
    pwd = st.text_input("Enter instructor password:", type="password")
    if pwd == "admin123":
        st.session_state['user_role'] = "instructor"
    else:
        st.warning("Please enter the correct password.")
elif role == "Student":
    name = st.text_input("Enter your name:")
    if name:
        st.session_state['user_role'] = "student"
        st.session_state['student_name'] = name

# Stop until role is chosen correctly
if not st.session_state['user_role']:
    st.stop()

# =========================
# HELPER FUNCTIONS
# =========================
def compute_metrics(mt_output, student_output, reference_output=None):
    """Compute basic text metrics."""
    start_time = time.time()

    bleu = sentence_bleu([reference_output.split()] if reference_output else [mt_output.split()],
                         student_output.split())
    chrf = sentence_chrf(reference_output if reference_output else mt_output, student_output)
    fluency = round(len(student_output.split()) / max(1, len(mt_output.split())), 2)
    accuracy = round(len(set(student_output.split()) & set(mt_output.split())) /
                     max(1, len(set(mt_output.split()))), 2)

    # diff
    diff = list(difflib.ndiff(mt_output.split(), student_output.split()))
    additions = sum(1 for d in diff if d.startswith('+ '))
    deletions = sum(1 for d in diff if d.startswith('- '))
    edits = additions + deletions

    end_time = time.time()
    duration = round(end_time - start_time, 2)
    keystrokes = len(student_output)

    return bleu, chrf, fluency, accuracy, additions, deletions, edits, duration, keystrokes

def highlight_edits(old, new):
    """Highlight only post-editing differences."""
    old_words = old.split()
    new_words = new.split()
    diff = list(difflib.ndiff(old_words, new_words))
    html = []
    for d in diff:
        if d.startswith('- '):
            html.append(f"<span style='background-color:#ffcccc;text-decoration:line-through;'>{d[2:]}</span> ")
        elif d.startswith('+ '):
            html.append(f"<span style='background-color:#ccffcc;'>{d[2:]}</span> ")
        else:
            html.append(d[2:] + " ")
    return ''.join(html)

# =========================
# AI FEEDBACK MODEL
# =========================
@st.cache_resource
def load_ai_model():
    model_name = "facebook/mbart-large-50"
    tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
    model = MBartForConditionalGeneration.from_pretrained(model_name)
    return tokenizer, model

def generate_ai_feedback(source_text, student_text, reference_text=None):
    tokenizer, model = load_ai_model()
    base_text = reference_text if reference_text else source_text
    prompt = (f"Evaluate this translation quality:\n\n"
              f"Source: {base_text}\n"
              f"Student translation: {student_text}\n\n"
              f"Give a short comment on fluency, accuracy, and style.")
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    summary_ids = model.generate(**inputs, max_length=100, num_beams=3, early_stopping=True)
    feedback = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return feedback

# =========================
# STUDENT INTERFACE
# =========================
if st.session_state['user_role'] == "student":
    st.subheader("Student Workspace")

    source_text = st.text_area("Source Text", height=100)
    mt_output = st.text_area("Machine Translation Output", height=100)
    reference_translation = st.text_area("Reference Translation (optional)", height=100)
    student_translation = st.text_area("Post-Edited Translation", height=100)

    if st.button("Submit Translation"):
        if source_text and mt_output and student_translation:
            bleu, chrf, fluency, accuracy, adds, dels, edits, duration, keystrokes = compute_metrics(
                mt_output, student_translation, reference_translation)
            st.session_state['student_translation'] = student_translation

            # Track changes (visible only for editing)
            diff_html = highlight_edits(mt_output, student_translation)
            st.markdown("### ✏️ Track Changes View")
            st.markdown(diff_html, unsafe_allow_html=True)

            # Metrics display
            st.write(f"**Fluency:** {fluency}")
            st.write(f"**Accuracy:** {accuracy}")
            st.write(f"**BLEU:** {bleu}")
            st.write(f"**chrF:** {chrf}")
            st.write(f"**Additions:** {adds}")
            st.write(f"**Deletions:** {dels}")
            st.write(f"**Edits:** {edits}")
            st.write(f"**Time Spent:** {duration} sec")
            st.write(f"**Keystrokes:** {keystrokes}")

            # AI feedback
            if st.button("Generate AI Feedback"):
                with st.spinner("Generating AI feedback..."):
                    feedback_text = generate_ai_feedback(source_text, student_translation, reference_translation)
                st.success("AI Feedback generated successfully ✅")
                st.write(f"**AI Comment:** {feedback_text}")

            # Store submission
            name = st.session_state['student_name']
            st.session_state['submissions'][name] = {
                "source": source_text,
                "mt": mt_output,
                "student": student_translation,
                "reference": reference_translation,
                "metrics": {
                    "fluency": fluency, "accuracy": accuracy, "BLEU": bleu, "chrF": chrf,
                    "additions": adds, "deletions": dels, "edits": edits,
                    "duration": duration, "keystrokes": keystrokes
                },
                "feedback": feedback_text if 'feedback_text' in locals() else ""
            }
        else:
            st.warning("Please fill in all required fields before submitting.")

# =========================
# INSTRUCTOR INTERFACE
# =========================
elif st.session_state['user_role'] == "instructor":
    st.subheader("Instructor Dashboard")

    if not st.session_state['submissions']:
        st.info("No student submissions yet.")
    else:
        student_names = list(st.session_state['submissions'].keys())
        selected_student = st.selectbox("Select a student:", student_names)

        data = st.session_state['submissions'][selected_student]
        st.write("### Source Text")
        st.write(data['source'])
        st.write("### MT Output")
        st.write(data['mt'])
        st.write("### Student Translation")
        st.write(data['student'])

        st.markdown("### 🔍 Post-Editing Changes")
        diff_html = highlight_edits(data['mt'], data['student'])
        st.markdown(diff_html, unsafe_allow_html=True)

        st.markdown("### 📊 Metrics")
        for k, v in data['metrics'].items():
            st.write(f"**{k.capitalize()}:** {v}")

        if data['feedback']:
            st.markdown("### 🤖 AI Feedback")
            st.write(data['feedback'])

        # Export to Word
        if st.button("Download Student Report"):
            doc = Document()
            doc.add_heading(f"Report for {selected_student}", level=1)
            doc.add_paragraph(f"Source Text:\n{data['source']}")
            doc.add_paragraph(f"Machine Translation:\n{data['mt']}")
            doc.add_paragraph(f"Student Translation:\n{data['student']}")
            doc.add_heading("Metrics", level=2)
            for k, v in data['metrics'].items():
                doc.add_paragraph(f"{k}: {v}")
            doc.add_heading("AI Feedback", level=2)
            doc.add_paragraph(data['feedback'])

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button(
                label="Download as Word",
                data=buffer,
                file_name=f"{selected_student}_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
