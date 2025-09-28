import string

def simple_accuracy(source_text, student_translation, synonyms=None):
    """
    Computes a rough accuracy score (0-1) by comparing words, allowing simple synonyms.
    synonyms: dict, e.g., {'car': ['automobile'], 'house':['home']}
    """
    if synonyms is None:
        synonyms = {}

    # Normalize text: lowercase and remove punctuation
    def normalize(text):
        return [w.strip(string.punctuation).lower() for w in text.split()]

    source_words = normalize(source_text)
    student_words = normalize(student_translation)

    matches = 0
    for w in student_words:
        if w in source_words:
            matches += 1
        else:
            # Check synonyms
            for key, syns in synonyms.items():
                if w in syns and key in source_words:
                    matches += 1
                    break

    if len(source_words) == 0:
        return 0.0
    return round(matches / len(source_words), 2)


def evaluate_translation(source_text, student_translation):
    """
    Evaluates fluency and accuracy of a student translation.
    Returns scores between 0 and 1.
    """
    # Fluency: length-based approximation
    fluency = min(1.0, len(student_translation.split()) / max(len(source_text.split()),1))

    # Accuracy: using simple word overlap + synonyms
    # Example synonym dictionary (expand as needed)
    synonyms = {
        "quick": ["fast"],
        "car": ["automobile"],
        "house": ["home"],
        "child": ["kid"]
    }
    accuracy = simple_accuracy(source_text, student_translation, synonyms)

    return round(fluency,2), round(accuracy,2)
