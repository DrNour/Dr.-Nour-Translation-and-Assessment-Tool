import time
import uuid

class PostEditSession:
    def __init__(self, exercise_text, student_name, exercise_id):
        self.id = str(uuid.uuid4())  # unique submission ID
        self.exercise_id = exercise_id
        self.student_name = student_name
        self.original_text = exercise_text
        self.edited_text = ""
        self.start_time = None
        self.end_time = None
        self.keystrokes = 0
        self.metrics = {
            "accuracy": None,
            "fluency": None,
            "edit_distance": None,
            "time_spent_sec": None,
            "keystrokes": None
        }

    def start_edit(self):
        self.start_time = time.time()

    def finish_edit(self, edited_text):
        self.end_time = time.time()
        self.edited_text = edited_text
        self.keystrokes = len(edited_text)
        self.evaluate()

    def evaluate(self):
        self.metrics["accuracy"] = len(self.edited_text) / max(len(self.original_text), 1)
        self.metrics["fluency"] = len(set(self.edited_text.split())) / max(len(self.edited_text.split()), 1) if self.edited_text else 0
        self.metrics["edit_distance"] = abs(len(self.original_text) - len(self.edited_text))
        self.metrics["time_spent_sec"] = round(self.end_time - self.start_time, 2) if self.start_time and self.end_time else 0
        self.metrics["keystrokes"] = self.keystrokes
        return self.metrics
