import streamlit as st
import os
import importlib.util

# import storage from same folder
BASE_DIR = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("storage", os.path.join(BASE_DIR, "storage.py"))
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)

def student_dashboard():
    st.title("🎓 Student Dashboard")

    student_name = st.text_input("Enter your name")
    student_group = st.selectbox("Select your group", ["Group A", "Group B", "Group C"])

    if not student_name.strip():
        st.warning("Please enter your name to continue.")
        return

    assignments = storage.load_assignments()
    submissions = storage.load_submissions()

    if not assignments:
        st.info("No assignments available yet.")
        return

    for a_id, a in assignments.items():
        if a.get("group", "all") in [student_group, "all"]:
            st.subheader(a["title"])
            st.write("📖 Instructions:", a.get("instructions", ""))
            st.write("✍️ Exercise:", a.get("text", ""))

            translation = st.text_area(f"Your Answer for {a['title']}", key=a_id)

            if st.button(f"Submit {a['title']}", key=f"btn_{a_id}"):
                storage.save_submissions(
                    assignment_title=a["title"],
                    translation=translation,
                    student_name=student_name,
                    group=student_group
                )
                st.success(f"✅ {student_name}, your submission has been saved!")

    if submissions:
        st.subheader("📂 Your Previous Submissions")
        for s_id, s in submissions.items():
            if s.get("student_name") == student_name:
                st.write(f"**{s['assignment_title']}**: {s['translation']}")
