import streamlit as st

def student_panel():
    st.header("Student Interface")
    translation = st.text_area("Submit your translation:")
    post_editing = st.checkbox("Post-editing mode")
    if st.button("Submit"):
        st.success("Translation submitted!")
