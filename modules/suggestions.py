def suggest_exercises(history):
    if not history:
        return ["Translate a news article.", "Post-edit a machine translation."]
    if history[-1]["score"] < 0.6:
        return ["Practice with shorter sentences.", "Focus on accuracy."]
    return ["Try literary text.", "Translate a technical manual."]
