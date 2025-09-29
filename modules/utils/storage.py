import json, os

ASSIGNMENTS_FILE = "data/assignments.json"

def load_assignments():
    if not os.path.exists(ASSIGNMENTS_FILE):
        return {}
    with open(ASSIGNMENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_assignments(assignments):
    with open(ASSIGNMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(assignments, f, indent=4)

def add_assignment(assignment):
    assignments = load_assignments()
    assignments[assignment["assignment_id"]] = assignment
    save_assignments(assignments)
