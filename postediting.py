import time

class PostEditSession:
    def __init__(self):
        self.start_time = time.time()
        self.keystrokes = 0

    def record_keystroke(self):
        self.keystrokes += 1

    def elapsed_time(self):
        return time.time() - self.start_time

def calculate_edit_distance(original, edited):
    # simple Levenshtein distance
    import numpy as np
    dp = np.zeros((len(original)+1, len(edited)+1))
    for i in range(len(original)+1):
        dp[i][0] = i
    for j in range(len(edited)+1):
        dp[0][j] = j
    for i in range(1,len(original)+1):
        for j in range(1,len(edited)+1):
            if original[i-1] == edited[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1])
    return dp[len(original)][len(edited)]

def calculate_edit_ratio(original, edited):
    return calculate_edit_distance(original, edited)/max(len(original), len(edited),1)

def highlight_errors(original, edited):
    errors = []
    for i, (o,e) in enumerate(zip(original, edited)):
        if o != e:
            errors.append((i,o,e))
    return errors
