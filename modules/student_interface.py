import streamlit as st
import time

try:
    from modules.postediting import calculate_edit_distance, calculate_edit_ratio
except ModuleNotFoundError:
    calculate_edit_distance = calculate_edit_ratio = None

def student_dashboard():
    st.header("Student Dashboard")

    # Input: Original text (can be optional)
    original_text = st.text_area("Text to Translate (optional)")

    # Input: Student translation
    student_translation = st.text_area("Your Translation")

    if st.button("Submit Translation"):
        if not student_translation.strip():
            st.warning("Please enter a translation before submitting.")
        else:
            st.success("Translation submitted successfully!")

            # Post-edit metrics (safe)
            if calculate_edit_distance and original_text.strip():
                distance = calculate_edit_distance(original_text, student_translation)
                ratio = calculate_edit_ratio(original_text, student_translation)
                st.write(f"Edit Distance: {distance}")
                st.write(f"Edit Ratio: {ratio:.2f}")
            else:
                st.info("Post-edit metrics unavailable (no original text or module missing).")
