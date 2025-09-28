# modules/evaluation.py

def evaluate_translation(source_text, student_translation):
    """
    Stub function to calculate fluency and accuracy.
    Replace this with your actual scoring logic.
    
    Returns:
        fluency (float): Fluency score between 0 and 1
        accuracy (float): Accuracy score between 0 and 1
    """
    # --- Example simple scoring logic ---
    # Fluency: fraction of words that are "well-formed"
    source_words = source_text.split()
    student_words = student_translation.split()

    # Prevent division by zero
    if len(student_words) == 0:
        fluency = 0.0
    else:
        fluency = min(1.0, len(student_words)/len(source_words))

    # Accuracy: fraction of words matching source words (very basic)
    common_words = sum(1 for w in student_words if w in source_words)
    accuracy = min(1.0, common_words / max(len(source_words),1))

    # Round scores to 2 decimals
    fluency = round(fluency, 2)
    accuracy = round(accuracy, 2)

    return fluency, accuracy
