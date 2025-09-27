import streamlit as st

def award_badges(score):
    badges = []
    if score > 90:
        badges.append("🌟 Expert Translator")
    elif score > 70:
        badges.append("🔥 Rising Star")
    else:
        badges.append("🎯 Beginner")
    st.subheader("🏅 Your Badges")
    for badge in badges:
        st.write(badge)
    return badges
