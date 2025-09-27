import streamlit as st

badges_awarded = {}

def award_badge(student_name, badge_name):
    if student_name not in badges_awarded:
        badges_awarded[student_name] = []
    if badge_name not in badges_awarded[student_name]:
        badges_awarded[student_name].append(badge_name)
        st.success(f"{student_name} earned badge: {badge_name}")
