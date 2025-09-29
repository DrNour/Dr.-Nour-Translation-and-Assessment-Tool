import os
import json

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

# Assignments
def load_assignments():
    return load_json(ASSIGNMENTS_FILE)

def save_assignments(assignments):
    save_json(ASSIGNMENTS_FILE, assignments)

# Submissions
def load_submissions():
    return load_json(SUBMISSIONS_FILE)

def save_submissions(assignment_title, translation, student_name=None, group=None):
    submissions = load_submissions()
    submission_id = f"{assignment_title}_{student_name or 'Anonymous'}_{len(submissions)+1}"
    submissions[submission_id] = {
        "assignment_title": assignment_title,
        "translation": translation,
        "student_name": student_name,
        "group": group
    }
    save_json(SUBMISSIONS_FILE, submissions)
