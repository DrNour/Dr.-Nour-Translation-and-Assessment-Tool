# modules/error_analysis.py
def categorize_errors(original, candidate):
    errors = []
    if original != candidate:
        if len(original.split()) != len(candidate.split()):
            errors.append("Length mismatch")
        if any(c.isupper() for c in candidate) and not any(o.isupper() for o in original):
            errors.append("Capitalization error")
    return errors
