import streamlit as st
import json
from pathlib import Path

LEADERBOARD_FILE = Path(__file__).parent / "leaderboard.json"

def load_leaderboard():
    if LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_leaderboard(student_name, score):
    leaderboard = load_leaderboard()
    leaderboard.append({"name": student_name, "score": score})
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:20]  # top 20
    save_leaderboard(leaderboard)

def show_leaderboard():
    leaderboard = load_leaderboard()
    if leaderboard:
        st.table(leaderboard)
    else:
        st.info("Leaderboard is empty.")

# --- Badge system ---
BADGES_FILE = Path(__file__).parent / "badges.json"

def load_badges():
    if BADGES_FILE.exists():
        with open(BADGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_badges(data):
    with open(BADGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def award_badges(student_name, score, ratio, time_spent):
    badges = load_badges()
    user_badges = badges.get(student_name, [])

    new_badges = []
    if time_spent < 60 and "Fast Translator" not in user_badges:
        user_badges.append("Fast Translator")
        new_badges.append("Fast Translator")
    if ratio < 0.2 and "Accurate Editor" not in user_badges:
        user_badges.append("Accurate Editor")
        new_badges.append("Accurate Editor")
    if score > 90 and "High Scorer" not in user_badges:
        user_badges.append("High Scorer")
        new_badges.append("High Scorer")

    badges[student_name] = user_badges
    save_badges(badges)

    return new_badges
