# gamification.py
def calculate_points(submission_quality: float, speed: float):
    """
    Example function to calculate points based on quality and speed.
    """
    points = int(submission_quality * 10 + speed * 5)
    return points

def assign_badge(points: int):
    if points > 50:
        return "Gold Badge"
    elif points > 30:
        return "Silver Badge"
    else:
        return "Bronze Badge"
