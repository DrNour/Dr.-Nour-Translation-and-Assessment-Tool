import streamlit as st
import os
import json
import uuid
import time
from difflib import SequenceMatcher
from docx import Document
from io import BytesIO

# ------------------ Data Setup ------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, "assignments.json")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.json")

def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_assignments():
    return load_json(ASSIGNMENTS_FILE)

def save_assignments(assignments):
    save_json(ASSIGNMENTS_FILE, assignments)

def load_submissions():
    return load_json(SUBMISSIONS_FILE)

def save_submissions(assignment_title, translation, student_name=None, group=None, stats=None):
    submissions = load_submissions()
    submission_id = f"{assignment_title}_{student_name or 'Anonymous'}_{len(submissions)+1}"
    submissions[submission_id] = {
        "assignment_title": assignment_title,
        "translation": translation,
        "student_name": student_name,
        "group": group,
        "stats": stats or {}
    }
    save_json(SUBMISSIONS_FILE, submissions)

# ------------------ Metrics ------------------
def calculate_metrics(source, translation, start_time, keystrokes, prev_translation=None):
    end_time = time.time()
    time_spent = round(end_time - start_time, 2)

    # Simple fluency & accuracy placeholders
    fluency = round(len(translation.split()) / max(1, len(source.split())), 2)
    accuracy = round(1 - (len(set(source.split()) - set(translation.split())) / max(1, len(source.split()))), 2)

    # Edits
    additions, omissions, edits = 0, 0, 0
    if prev_translation:
        s = prev_translation.split()
        t = translation.split()
        sm = SequenceMatcher(None, s, t)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'replace':
                edits += max(i2-i1, j2-j1)
            elif tag == 'delete':
                omissions += i2 - i1
            elif tag == 'insert':
                additions += j2 - j1

    return {
        "fluency": fluency,
        "accuracy": accuracy,
        "time_spent_sec": time_spent,
        "keystrokes": keystrokes,
        "additions": additions,
        "omissions": omissions,
        "edits": edits
    }

# ------------------ Streamlit App ------------------
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["Student", "Instructor"])

if choice == "Student":
    st.title("🎓 Student Dashboard")

    student_name = st.text_input("Enter your name")
    student_group = st.selectbox("Select your group", ["Group A", "Group B", "Group C"])

    if student_name.strip():
        assignments = load_assignments()
        submissions = load_submissions()

        if not assignments:
            st.info("No assignments available yet.")
        else:
            for a_id, a in assignments.items():
                if a.get("group", "all") in [student_group, "all"]:
                    st.subheader(a["title"])
                    st.write("📖 Instructions:", a.get("instructions", ""))
                    st.write("✍️ Exercise:", a.get("text", ""))

                    prev_translation = None
                    for s in submissions.values():
                        if s.get("student_name")==student_name and s.get("assignment_title")==a["title"]:
                            prev_translation = s["translation"]

                    # Time & keystrokes
                    if f"start_{a_id}" not in st.session_state:
                        st.session_state[f"start_{a_id}"] = time.time()
                    if f"keystrokes_{a_id}" not in st.session_state:
                        st.session_state[f"keystrokes_{a_id}"] = 0

                    def count_keys():
                        st.session_state[f"keystrokes_{a_id}"] += 1

                    translation = st.text_area(
                        f"Your Answer for {a['title']}", 
                        value=prev_translation or "", 
                        key=a_id, 
                        on_change=count_keys
                    )

                    if st.button(f"Submit {a['title']}", key=f"btn_{a_id}"):
                        stats = calculate_metrics(
                            source=a["text"],
                            translation=translation,
                            start_time=st.session_state[f"start_{a_id}"],
                            keystrokes=st.session_state[f"keystrokes_{a_id}"],
                            prev_translation=prev_translation
                        )
                        save_submissions(
                            assignment_title=a["title"],
                            translation=translation,
                            student_name=student_name,
                            group=student_group,
                            stats=stats
                        )
                        st.success(f"✅ {student_name}, your submission has been saved!")
                        st.json(stats)

        # Show previous submissions
        st.subheader("📂 Your Previous Submissions")
        for s_id, s in submissions.items():
            if s.get("student_name") == student_name:
                st.write(f"**{s['assignment_title']}**: {s['translation']}")
                st.write(f"Metrics: {s.get('stats', {})}")

    else:
        st.warning("Please enter your name to continue.")

else:  # Instructor
    st.title("📘 Instructor Dashboard")

    st.subheader("Create New Assignment")
    title = st.text_input("Assignment Title")
    text = st.text_area("Assignment Text")
    instructions = st.text_area("Instructions")
    group = st.selectbox("Assign to Group", ["all", "Group A", "Group B", "Group C"])

    if st.button("Save Assignment"):
        if title.strip() and text.strip():
            assignments = load_assignments()
            assignment_id = str(uuid.uuid4())
            assignments[assignment_id] = {
                "id": assignment_id,
                "title": title,
                "text": text,
                "instructions": instructions,
                "group": group
            }
            save_assignments(assignments)
            st.success(f"Assignment '{title}' created successfully!")

    st.subheader("📂 Existing Assignments")
    assignments = load_assignments()
    if assignments:
        for a in assignments.values():
            st.write(f"**{a['title']}** (Group: {a['group']})")
            st.write(a.get("instructions", ""))
            st.write(a.get("text", ""))
            st.markdown("---")
    else:
        st.info("No assignments yet.")

    st.subheader("📥 Student Submissions")
    submissions = load_submissions()
    if submissions:
        for s in submissions.values():
            st.write(f"**{s['student_name']}** ({s['group']}) - {s['assignment_title']}")
            st.write(f"✍️ {s['translation']}")
            st.write(f"Metrics: {s.get('stats', {})}")
            st.markdown("---")

        # ------------------ Download Word ------------------
        if st.button("Download All Submissions as Word"):
            doc = Document()
            for s in submissions.values():
                doc.add_heading(f"{s['assignment_title']} - {s['student_name']}", level=2)
                doc.add_paragraph(s['translation'])
                doc.add_paragraph(f"Metrics: {s.get('stats', {})}")
                doc.add_paragraph("-"*50)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button(
                label="Download Submissions.docx",
                data=buffer,
                file_name="submissions.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.info("No submissions yet.")
