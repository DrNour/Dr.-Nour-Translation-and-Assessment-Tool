import streamlit as st

# leaderboard_data persists across sessions
leaderboard_data = {"Alice": 10, "Bob": 8}

def leaderboard():
    st.subheader("Leaderboard")
    sorted_board = sorted(leaderboard_data.items(), key=lambda x: x[1], reverse=True)
    for name, points in sorted_board:
        st.write(f"{name}: {points} points")
