import os
import json

DATA_DIR = "data"
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, "assignments.json")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---- Assignments ----
def load_assignments():
    return load_json(ASSIGNMENTS_FILE)

def save_assignments(data):
    save_json(ASSIGNMENTS_FILE, data)

# ---- Submissions ----
def load_submissions():
    return load_json(SUBMISSIONS_FILE)

def save_submissions(data):
    save_json(SUBMISSIONS_FILE, data)
