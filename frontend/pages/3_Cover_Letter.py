import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import streamlit as st
from app.cover_letter_generator import generate_cover_letter
from io import BytesIO
from docx import Document
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="AI Cover Letter Generator", layout="wide")
st.title("AI Cover Letter Generator")

if "resume_json" not in st.session_state:
    st.warning("Please upload your resume first.")
    st.stop()

resume = st.session_state.resume_json

# Personalization Inputs
st.subheader("Personalization")
user_name = st.text_input("Your Name", placeholder="e.g., xyz").strip()
location = st.text_input("Your Location", placeholder="e.g., Chennai, India").strip()
experience = st.text_input("Years of Experience", placeholder="e.g., 1 year").strip()
project_highlights = st.text_area("Project Highlights / Achievements", placeholder="e.g., Built a scalable product for 5k users").strip()

# Job Inputs
st.subheader("Job Details")
job_title = st.text_input("Job Title", placeholder="e.g., Full Stack Developer").strip()
company = st.text_input("Company Name", placeholder="e.g., Cognizant").strip()
job_description = st.text_area("Job Description", height=200).strip()

tone = st.selectbox("Select Tone", ["Formal", "Friendly", "Confident"])
paragraphs = st.selectbox("Cover Letter Length", ["1 Paragraph", "2 Paragraphs","3 Paragraphs"])

# Generate Cover Letter
if st.button("Generate Cover Letter"):
    if not job_title or not company or not job_description:
        st.error("Please complete all job fields.")
    else:
        with st.spinner("Crafting your personalized cover letter..."):
            # Extend resume data with personalized fields
            resume["location"] = location
            resume["experience"] = experience
            resume["projects"] = project_highlights

            letter = generate_cover_letter(
                resume, job_description, company, job_title, tone, paragraphs
            )
            st.session_state.generated_letter = letter

# Editable Preview
if "generated_letter" in st.session_state:
    st.subheader("Edit Your Cover Letter")

    edited_letter = st.session_state.generated_letter
    if user_name:
        edited_letter = edited_letter.replace("[Your Name]", user_name)

    edited_letter = st.text_area("Edit before exporting:", value=edited_letter, height=300)
    st.session_state.generated_letter = edited_letter

    st.subheader("Export Options")

    # TXT Export
    st.download_button("Download as TXT", edited_letter, file_name="cover_letter.txt")

    # PDF Export
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in edited_letter.split("\n"):
            pdf.multi_cell(0, 10, line)
        pdf.output(tmp_pdf.name)
        tmp_pdf.seek(0)
        st.download_button("Download as PDF", tmp_pdf.read(), file_name="cover_letter.pdf")

    # DOCX Export
    doc = Document()
    doc.add_paragraph(edited_letter)
    doc_buffer = BytesIO()
    doc.save(doc_buffer)
    doc_buffer.seek(0)
    st.download_button("Download as Word (.docx)", doc_buffer, file_name="cover_letter.docx")


