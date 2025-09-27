import streamlit as st

def leaderboard():
    st.subheader("🏆 Leaderboard")
    scores = {"Ali": 85, "Mona": 92, "Yousef": 78}
    for name, score in scores.items():
        st.write(f"{name}: {score} points")
