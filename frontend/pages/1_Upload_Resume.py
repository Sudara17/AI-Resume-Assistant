# frontend/pages/1_Upload_Resume.py
import os
import streamlit as st
import fitz  # PyMuPDF
from app.structured_extractor import extract_resume_json

st.set_page_config(page_title="Upload Resume", layout="wide")
st.title("Upload Resume")

uploaded_file = st.file_uploader("Upload a Resume (PDF)", type=["pdf"], help="Limit 200MB per file • PDF")
if not uploaded_file:
    st.info("Please upload a PDF resume to continue.")
    st.stop()

# Save uploaded file to a temp path so we can read with PyMuPDF
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)
saved_path = os.path.join(upload_dir, uploaded_file.name)
with open(saved_path, "wb") as f:
    f.write(uploaded_file.getbuffer())

st.success("Resume file uploaded successfully")

# Extract text using PyMuPDF
def extract_text_from_pdf(path: str) -> str:
    text = ""
    try:
        with fitz.open(path) as doc:
            for page in doc:
                page_text = page.get_text("text")
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
    return text

with st.spinner("Resume text extracted"):
    resume_text = extract_text_from_pdf(saved_path)
    if not resume_text.strip():
        st.error("Could not extract text from the uploaded PDF. Try a different resume.")
        st.stop()
    st.success("Resume text extracted")

# Parse using your existing structured extractor (returns JSON/dict)
with st.spinner("Resume parsed to JSON"):
    parsed_json = extract_resume_json(resume_text)
    st.success("Resume parsed to JSON")

# Display extracted JSON (collapsible)
st.subheader("Extracted Resume Data")
st.json(parsed_json)

# Save into session state so other pages (chatbot etc.) can reuse it
st.session_state["resume_text"] = resume_text
st.session_state["resume_filename"] = uploaded_file.name
st.session_state["parsed_resume_json"] = parsed_json

st.info("Resume stored for other modules (Chatbot, ATS Insights, Cover Letter).")
