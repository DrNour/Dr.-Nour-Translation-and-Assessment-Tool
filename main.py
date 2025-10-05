import streamlit as st
import pandas as pd
import time
import difflib
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.chrf_score import sentence_chrf
from io import BytesIO
from docx import Document
from docx.shared import RGBColor
import base64
import random

# =====================================================
# Initialize session state
# =====================================================
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}
if 'submissions' not in st.session_state:
    st.session_state.submissions = {}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# =====================================================
# Helper Functions
# =====================================================

def evaluate_translation(mt_output, post_edit, reference=None):
    """Calculate metrics with improved diff detection."""
    fluency = len(post_edit.split()) / max(len(mt_output.split()), 1)
    accuracy = difflib.SequenceMatcher(None, mt_output, post_edit).ratio()

    bleu = None
    chrf = None
    if reference:
        smoothie = SmoothingFunction().method4
        bleu = sentence_bleu([reference.split()], post_edit.split(), smoothing_function=smoothie)
        chrf = sentence_chrf([reference], post_edit)
    
    diff = list(difflib.ndiff(mt_output.split(), post_edit.split()))
    additions = sum(1 for word in diff if word.startswith('+ '))
    deletions = sum(1 for word in diff if word.startswith('- '))
    edits = additions + deletions

    return {
        "Fluency": round(fluency, 2),
        "Accuracy": round(accuracy, 2),
        "BLEU": round(bleu, 2) if bleu is not None else None,
        "chrF": round(chrf, 2) if chrf is not None else None,
        "Additions": additions,
        "Deletions": deletions,
        "Edits": edits
    }

def highlight_diff(original, edited):
    """Highlight differences between MT output and student edits."""
    diff = difflib.ndiff(original.split(), edited.split())
    highlighted = []
    for word in diff:
        if word.startswith('- '):
            highlighted.append(f"<span style='color:red;text-decoration:line-through'>{word[2:]}</span>")
        elif word.startswith('+ '):
            highlighted.append(f"<span style='color:green;font-weight:bold'>{word[2:]}</span>")
        else:
            highlighted.append(word[2:])
    return ' '.join(highlighted)

def generate_ai_feedback(metrics):
    """AI-like feedback based on metrics."""
    flu, acc, edits = metrics["Fluency"], metrics["Accuracy"], metrics["Edits"]
    feedback = []

    if flu < 0.8:
        feedback.append("Your translation seems slightly shorter or less fluent than expected. Try improving cohesion.")
    elif flu > 1.2:
        feedback.append("Your text is much longer than the machine output. Ensure additions enhance clarity.")
    else:
        feedback.append("Fluency looks balanced — well done maintaining flow.")

    if acc < 0.8:
        feedback.append("Accuracy could improve. Review terminology consistency and word order.")
    else:
        feedback.append("Accuracy is strong. Keep maintaining lexical precision.")

    if edits > 10:
        feedback.append("You made many edits — good engagement! Reflect if all were necessary for meaning.")
    elif edits < 3:
        feedback.append("Few edits — check if you missed subtle MT errors or style mismatches.")

    return " ".join(feedback)

def suggest_ai_exercise(metrics):
    """Suggest AI-generated exercise ideas."""
    exercises = []
    if metrics["Fluency"] < 0.9:
        exercises.append("Practice rewriting machine-translated sentences to sound more natural in context.")
    if metrics["Accuracy"] < 0.85:
        exercises.append("Review word choice exercises — focus on semantic precision and collocations.")
    if metrics["Edits"] > 10:
        exercises.append("Try a minimal post-editing challenge: fix meaning only, not style.")
    if not exercises:
        exercises.append("Try translating culturally loaded phrases and compare with MT outputs.")
    return random.choice(exercises)

def download_word_file(text, filename="translation_feedback.docx"):
    """Download text as Word file."""
    doc = Document()
    doc.add_paragraph(text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📄 Download Word File</a>'
    return href

# =====================================================
# Authentication
# =====================================================
st.sidebar.title("User Access")

if not st.session_state.logged_in:
    role = st.sidebar.selectbox("Select Role", ["Student", "Instructor"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password" if role == "Instructor" else "default")

    if st.sidebar.button("Login"):
        if role == "Instructor" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "Instructor"
            st.session_state.current_user = username
        elif role == "Student":
            st.session_state.logged_in = True
            st.session_state.role = "Student"
            st.session_state.current_user = username
        else:
            st.sidebar.error("Invalid credentials.")

else:
    st.sidebar.success(f"Logged in as {st.session_state.role}: {st.session_state.current_user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.current_user = None
        st.rerun()

# =====================================================
# Instructor Panel
# =====================================================
if st.session_state.logged_in and st.session_state.role == "Instructor":
    st.title("Instructor Dashboard")
    st.subheader("Manage Assignments and Submissions")

    with st.expander("➕ Create New Assignment"):
        task_title = st.text_input("Assignment Title")
        source_text = st.text_area("Source Text")
        mt_output = st.text_area("Machine Translation Output")
        ref_translation = st.text_area("Optional Reference Translation (for BLEU/chrF)")

        if st.button("Create Assignment"):
            st.session_state.assignments[task_title] = {
                "source_text": source_text,
                "mt_output": mt_output,
                "reference": ref_translation
            }
            st.success("Assignment created successfully!")

    st.divider()
    st.subheader("📥 Submissions Review")

    for assignment, content in st.session_state.assignments.items():
        st.markdown(f"### 📝 {assignment}")
        subs = [s for s in st.session_state.submissions.values() if s['assignment'] == assignment]
        if not subs:
            st.info("No submissions yet.")
        else:
            for sub in subs:
                with st.expander(f"👤 {sub['student']}"):
                    st.markdown("**Post-Edited Text:**")
                    st.markdown(sub["post_edit"], unsafe_allow_html=True)
                    st.markdown("**Tracked Changes:**", unsafe_allow_html=True)
                    st.markdown(highlight_diff(content["mt_output"], sub["post_edit"]), unsafe_allow_html=True)

                    for k, v in sub["metrics"].items():
                        if v is not None:
                            st.write(f"{k}: {v}")

                    st.markdown(f"⏱️ Time: {round(sub['time'], 2)} sec | ⌨️ Keystrokes: {sub['keystrokes']}")

                    # AI feedback and exercise
                    st.info("🧠 " + sub["ai_feedback"])
                    st.success("💡 Suggested Exercise: " + sub["ai_exercise"])

                    st.markdown(download_word_file(sub["post_edit"], f"{sub['student']}_{assignment}.docx"), unsafe_allow_html=True)

# =====================================================
# Student Panel
# =====================================================
elif st.session_state.logged_in and st.session_state.role == "Student":
    st.title("Student Translation & Post-Editing Workspace")

    if not st.session_state.assignments:
        st.warning("No assignments available yet.")
    else:
        assignment = st.selectbox("Select Assignment", list(st.session_state.assignments.keys()))
        data = st.session_state.assignments[assignment]
        st.write("### Source Text")
        st.write(data["source_text"])
        st.write("### Machine Translation Output")
        st.write(data["mt_output"])

        st.divider()
        st.write("### Edit the MT Output Below")
        post_edit = st.text_area("Your Post-Edited Translation")
        start_time = time.time()

        if st.button("Submit"):
            end_time = time.time()
            time_spent = end_time - start_time
            keystrokes = len(post_edit)

            metrics = evaluate_translation(data["mt_output"], post_edit, data["reference"] or None)
            ai_feedback = generate_ai_feedback(metrics)
            ai_exercise = suggest_ai_exercise(metrics)

            st.session_state.submissions[f"{st.session_state.current_user}_{assignment}"] = {
                "student": st.session_state.current_user,
                "assignment": assignment,
                "post_edit": post_edit,
                "metrics": metrics,
                "time": time_spent,
                "keystrokes": keystrokes,
                "ai_feedback": ai_feedback,
                "ai_exercise": ai_exercise
            }

            st.success("✅ Submission recorded successfully!")
            st.write("### Your Metrics")
            for k, v in metrics.items():
                if v is not None:
                    st.write(f"{k}: {v}")
            st.info("🧠 " + ai_feedback)
            st.success("💡 Suggested Exercise: " + ai_exercise)

            st.markdown(download_word_file(post_edit, f"{st.session_state.current_user}_{assignment}.docx"), unsafe_allow_html=True)
