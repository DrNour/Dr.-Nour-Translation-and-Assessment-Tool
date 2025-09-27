import time
import textdistance

def calculate_edit_distance(ref, hyp):
    return textdistance.levenshtein(ref, hyp)

def track_edit_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    return wrapper
