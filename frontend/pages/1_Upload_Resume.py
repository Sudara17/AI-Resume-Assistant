import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.structured_extractor import extract_resume_json
import streamlit as st
from app.resume_parser import extract_text_from_pdf

st.set_page_config(page_title="Upload Resume", layout="wide")
st.title(" Upload a Resume")

uploaded_file = st.file_uploader("Upload a Resume (PDF)", type=["pdf"])

# Run extraction only on new file
if uploaded_file and (uploaded_file.name != st.session_state.get("resume_filename")):
    st.success(" Resume file uploaded successfully")

    raw_text = extract_text_from_pdf(uploaded_file)
    st.success(" Resume text extracted")

    with st.spinner(" Extracting structured resume data using LLM..."):
        resume_json = extract_resume_json(raw_text)

    st.success(" Resume parsed to JSON")

    # Save in session state
    st.session_state.resume_filename = uploaded_file.name
    st.session_state.resume_text = raw_text
    st.session_state.resume_json = resume_json

# Show previously extracted data if exists
if "resume_json" in st.session_state:
    st.subheader(" Extracted Resume Data")
    if "error" in st.session_state.resume_json:
        st.error(f" JSON Parse Error: {st.session_state.resume_json['error']}")
    else:
        st.json(st.session_state.resume_json)
else:
    st.info(" Please upload a resume to view parsed information.")



