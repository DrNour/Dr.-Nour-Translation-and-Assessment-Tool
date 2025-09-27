import streamlit as st
from modules.postedit_metrics import PostEditSession, calculate_edit_distance, highlight_errors

# Minimal error type simulation
def error_types(original, edited):
    errors = highlight_errors(original, edited)
    categorized = {"Substitution": [], "Insertion": [], "Deletion": []}
    for idx,o,e in errors:
        if e == "":
            categorized["Deletion"].append((idx,o))
        elif o == "":
            categorized["Insertion"].append((idx,e))
        else:
            categorized["Substitution"].append((idx,o,e))
    return categorized

def postedit_dashboard(student_name="Student"):
    st.subheader("Post-edit MT Output")
    mt_output = st.text_area("Machine-translated text")
    postedit_session = PostEditSession()
    edited_text = st.text_area("Edit here")
    
    if st.button("Submit Post-edit"):
        distance = calculate_edit_distance(mt_output, edited_text)
        st.write(f"Edit distance: {distance}")
        st.write(f"Time spent: {postedit_session.elapsed_time():.2f}s")
        st.write(f"Keystrokes: {postedit_session.keystrokes}")
        
        # Error type display
        errors = error_types(mt_output, edited_text)
        st.write("Error types identified:")
        for k,v in errors.items():
            st.write(f"{k}: {v}")

        # Update gamification points
        from modules.gamification import leaderboard_data
        points_earned = max(10 - distance, 0)
        if student_name in leaderboard_data:
            leaderboard_data[student_name] += points_earned
        else:
            leaderboard_data[student_name] = points_earned
        st.success(f"Points earned: {points_earned}")
