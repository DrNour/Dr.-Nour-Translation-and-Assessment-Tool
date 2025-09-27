import streamlit as st
from modules.badges import award_badge

leaderboard_data = {}

def award_points(student_name, points):
    if student_name not in leaderboard_data:
        leaderboard_data[student_name] = 0
    leaderboard_data[student_name] += points
    if leaderboard_data[student_name] >= 50:
        award_badge(student_name, "Top Translator")

def leaderboard():
    st.subheader("Leaderboard")
    for student, points in sorted(leaderboard_data.items(), key=lambda x: -x[1]):
        st.write(f"{student}: {points} points")
