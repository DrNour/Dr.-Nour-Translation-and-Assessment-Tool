import streamlit as st

# Temporary storage (replace with database later if needed)
if "translations" not in st.session_state:
    st.session_state["translations"] = []

def student_dashboard():
    st.title("Student Dashboard")

    # Example: Preloaded Source Text (ST)
    st.subheader("Source Text (ST)")
    source_text = """Eight short texts (ranging from 200 to 300 words) 
    were chosen from opinion columns, news articles, and literary excerpts. 
    These texts were pre-tested for readability and lexical difficulty 
    to ensure they were comparable across tasks."""
    st.write(source_text)

    # Input area for student's translation
    st.subheader("Your Translation")
    student_translation = st.text_area("Write your translation here:", height=200)

    # Save button
    if st.button("Save Translation"):
        if student_translation.strip():
            st.session_state["translations"].append({
                "source_text": source_text,
                "translation": student_translation
            })
            st.success("✅ Your translation has been saved!")

    # Comparison View
    if student_translation.strip():
        st.subheader("Comparison View")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Source Text**")
            st.write(source_text)

        with col2:
            st.markdown("**Your Translation**")
            st.write(student_translation)

    # Show previously saved translations
    if st.session_state["translations"]:
        st.subheader("📂 Your Saved Translations")
        for i, entry in enumerate(st.session_state["translations"], 1):
            st.markdown(f"**Exercise {i}:**")
            st.markdown(f"- **Source Text:** {entry['source_text']}")
            st.markdown(f"- **Translation:** {entry['translation']}")
            st.markdown("---")
