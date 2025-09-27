# modules/gamification.py
import streamlit as st

def leaderboard():
    st.subheader("Leaderboard")
    # Dummy leaderboard
    st.table([
        {"Student": "Alice", "Score": 95},
        {"Student": "Bob", "Score": 88},
        {"Student": "Charlie", "Score": 76},
    ])
