import streamlit as st
import time

# Dummy MT output function (replace with real MT API if desired)
def get_mt_output(source_text):
    # For demonstration, just reverse the text
    return source_text[::-1]

def postedit_dashboard():
    st.header("Student Post-Editing Interface")

    # Step 1: Input source text
    source_text = st.text_area("Enter the source text to translate:", height=150)

    if source_text:
        # Step 2: Choose mode
        mode = st.radio("Choose your translation mode:", ["Translate from scratch", "Post-edit MT output"])

        # Step 3: Show text box for translation
        if mode == "Translate from scratch":
            student_translation = st.text_area("Your Translation:", height=150)
        else:
            mt_output = get_mt_output(source_text)
            student_translation = st.text_area("Post-edit MT Output:", value=mt_output, height=150)

        # Step 4: Track time
        if "start_time" not in st.session_state:
            st.session_state.start_time = time.time()

        # Step 5: Submit button
        if st.button("Submit Translation"):
            elapsed_time = time.time() - st.session_state.start_time
            st.success("Translation submitted successfully!")
            st.write(f"Time spent (seconds): {round(elapsed_time, 2)}")
            
            # Optionally: store submission, mode, and elapsed_time in database or file
            submission = {
                "source_text": source_text,
                "student_translation": student_translation,
                "mode": mode,
                "time_spent": elapsed_time
            }
            st.json(submission)
            
            # Reset timer
            st.session_state.start_time = time.time()
