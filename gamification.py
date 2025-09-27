import streamlit as st

def show_leaderboard(data):
    st.subheader("Leaderboard")
    st.table(data)
