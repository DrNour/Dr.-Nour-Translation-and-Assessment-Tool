def analyze_errors(source, target):
    errors = []
    if not target:
        errors.append("Empty translation")
    if source.split()[:2] == target.split()[:2]:
        errors.append("Literal translation detected")
    if len(target.split()) < len(source.split()) * 0.5:
        errors.append("Possible omission")
    return errors
