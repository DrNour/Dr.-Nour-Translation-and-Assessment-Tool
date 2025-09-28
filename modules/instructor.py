import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def instructor_dashboard():
    st.title("Instructor Dashboard")
    st.write("Review and export student submissions.")

    # Access stored translations
    if "translations" not in st.session_state or not st.session_state["translations"]:
        st.warning("⚠️ No student submissions yet.")
        return

    submissions = st.session_state["translations"]

    # Display submissions
    st.subheader("📂 Student Submissions")
    for i, entry in enumerate(submissions, 1):
        st.markdown(f"**Exercise {i}:**")
        st.markdown(f"- **Source Text:** {entry['source_text']}")
        st.markdown(f"- **Translation:** {entry['translation']}")
        st.markdown("---")

    # Convert to DataFrame
    df = pd.DataFrame(submissions)

    # --- Excel Export ---
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Submissions")
        return output.getvalue()

    # --- Word Export ---
    def to_word(df):
        output = BytesIO()
        doc = Document()
        doc.add_heading("Student Submissions", 0)
        for i, row in df.iterrows():
            doc.add_heading(f"Exercise {i+1}", level=1)
            doc.add_paragraph(f"Source Text: {row['source_text']}")
            doc.add_paragraph(f"Translation: {row['translation']}")
        doc.save(output)
        return output.getvalue()

    # --- PDF Export ---
    def to_pdf(df):
        output = BytesIO()
        doc = SimpleDocTemplate(output)
        styles = getSampleStyleSheet()
        elements = [Paragraph("Student Submissions", styles['Title']), Spacer(1, 12)]
        for i, row in df.iterrows():
            elements.append(Paragraph(f"<b>Exercise {i+1}</b>", styles['Heading2']))
            elements.append(Paragraph(f"Source Text: {row['source_text']}", styles['Normal']))
            elements.append(Paragraph(f"Translation: {row['translation']}", styles['Normal']))
            elements.append(Spacer(1, 12))
        doc.build(elements)
        return output.getvalue()

    st.subheader("⬇️ Download Submissions")
    st.download_button("Download as Excel", to_excel(df), "submissions.xlsx")
    st.download_button("Download as Word", to_word(df), "submissions.docx")
    st.download_button("Download as PDF", to_pdf(df), "submissions.pdf")
