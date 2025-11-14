# ATS_INSIGHTS.PY (Full Final Code with Fixes)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import re
import altair as alt
import requests
import json

from app.jd_keywords import JD_KEYWORDS
from app.ats_score import calculate_ats_score
from app.groq_llm import get_groq_llm

# LangChain (fixed)
from langchain_core.prompts import PromptTemplate


# Resume Summary Analysis (LLM)
def check_summary_alignment(summary_text, role, api_key):
    prompt = PromptTemplate.from_template("""
You are a career coach. Given the candidate's resume summary and the target job role, evaluate how well the summary aligns.

Resume Summary:
{summary}

Target Job Role: {role}

Return one of the following:
- " Strong alignment"
- " Moderate alignment"
- " Poor alignment"

Also give a 1–2 sentence explanation.
""")

    llm = ChatGroq(api_key=api_key, model_name="llama3-8b-8192")
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run({"summary": summary_text, "role": role})

# Grammar & Spelling Checker using TextGears with whitelist
def grammar_and_spelling_feedback(text):
    url = "https://api.textgears.com/grammar"
    textgears_api_key = os.environ.get("TEXTGEARS_API_KEY")

    TECH_TERMS = {
        "css", "js", "html", "sql", "mysql", "nosql", "api", "apis", "restful",
        "mongodb", "postgresql", "fastapi", "jwt", "redux", "oop", "oops", "dsa",
        "ci/cd", "etl", "sdk", "json", "xml", "sass", "pwa", "npm", "nodejs", "expressjs",
        "github", "flutter", "react", "reactjs", "angular", "vue", "mern", "nextjs", "vite",
        "tailwind", "bootstrap", "figma", "git", "tensorflow", "keras", "pytorch", "huggingface",
        "openai", "langchain", "llamaindex", "chromadb", "faiss", "qdrant", "firebase",
        "spacy", "opencv", "llm", "rag", "ragchain", "nlp","sst","tts","smtp"
    }

    PLATFORMS = {
        "leetcode", "geeksforgeeks", "hackerrank", "github", "linkedin", "chatgpt",
        "estateease", "foodmunch", "technophilia"
    }

    ABBREVIATIONS = {
        "b.tech", "m.tech", "b.sc", "m.sc","bsc","msc", "ph.d", "cgpa", "ssl", "tls", "https", "html5",
        "css3", "xml", "json", "pdf", "ui", "ux", "cv", "gpa", "tcp", "ip", "dns", "llm", "rag", "doc","pdf","ppt"
    }

    NAMES_AND_LOCATIONS = {
        "sathak", "tiruchirappalli", "sudara", "souza", "bhavini", "rajavel", "kalpakkam",
        "chennai", "coimbatore", "chen", "mohammed", "sss", "ssn", "eee", "btech",
        "value", "healthsol", "axiom", "bsnl", "pci", "tamilnadu", "india"
    }

    OTHER_ALLOWED = {
        "optimized", "organize", "customized", "real-time", "frontend", "backend", "fullstack",
        "document-based", "ai-powered", "low-performing", "cross-functional", "naive",
        "agentic", "salesforce", "hcp", "medicode", "pipeline", "embedding"
    }

    FULL_WHITELIST = TECH_TERMS | PLATFORMS | ABBREVIATIONS | NAMES_AND_LOCATIONS | OTHER_ALLOWED

    def clean_word(w):
        return re.sub(r'[^a-zA-Z0-9\-]', '', w).lower()

    words = re.findall(r"\b[\w\-\.@]+\b", text)
    cleaned_words = []

    for word in words:
        lowered = clean_word(word)

        if not lowered:
            continue

        if "@" in word or any(char.isdigit() for char in word):
            continue

        parts = re.split(r"[-_]", lowered)
        if any(part in FULL_WHITELIST for part in parts) or lowered in FULL_WHITELIST:
            continue

        cleaned_words.append(word)

    filtered_text = " ".join(cleaned_words)

    params = {
        "text": filtered_text,
        "language": "en-GB",
        "key": api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
    except Exception as e:
        return [f"API error: {str(e)}"]

    suggestions = []
    if data.get("response", {}).get("errors"):
        for error in data["response"]["errors"]:
            bad = error["bad"]
            better = ", ".join(error.get("better", [])) or "No suggestion"
            suggestions.append(f" *{bad}* →  {better}")
    else:
        suggestions.append(" No grammar or spelling issues found.")

    return suggestions

# Streamlit UI
st.set_page_config(page_title="ATS Insights")
st.title(" ATS Resume Insights")

if "resume_text" not in st.session_state or "resume_json" not in st.session_state:
    st.warning("Please upload a resume first.")
    st.stop()

resume_text = st.session_state.resume_text
resume_json = st.session_state.resume_json

# Groq API Key
groq_api_key = os.environ.get("GROQ_API_KEY")

# Job Role Dropdown
job_roles = list(JD_KEYWORDS.keys())
job_roles.append("Other (Enter Custom Role)")

selected_role = st.selectbox("Select Job Role for Matching", job_roles)

custom_keywords = []
if selected_role == "Other (Enter Custom Role)":
    selected_role = st.text_input("Enter your custom job role")
    custom_kw_input = st.text_area("Enter relevant keywords (comma separated)")
    custom_keywords = [k.strip() for k in custom_kw_input.split(",") if k.strip()]

keywords = JD_KEYWORDS.get(selected_role, custom_keywords)

keywords = [k.lower().strip() for k in keywords if k.strip()]

# Summary Alignment First 
summary_text = resume_json.get("summary") or resume_json.get("projects", [{}])[0].get("description", "")
if summary_text:
    with st.spinner("Checking alignment..."):
        alignment_rating = check_summary_alignment(summary_text, selected_role, groq_api_key)
        st.info(alignment_rating)
else:
    alignment_rating = "Poor alignment"
    st.warning("No summary section found in resume.")

# Resume_data
resume_data = st.session_state.resume_json  

# Score Breakdown
total_score, score_breakdown, matched_skills = calculate_ats_score(
    resume_data , role_name=selected_role, alignment_rating=alignment_rating
)

# Display Score
st.metric(" ATS Compatibility Score", f"{total_score}/100")

for section, val in score_breakdown.items():
    if section == "Skills Match":
        continue  # Redundant now, but still safe

    if section in ["Education", "Contact Info", "Additional Contributions"]:
        max_val = 10
    else:
        max_val = 20

    st.markdown(f"**{section}:** {val}/{max_val}")

# Suggestions Box
st.subheader(" Suggestions for Improvement")
suggestions = []

if score_breakdown.get("Additional Contributions", 0) == 0:
    suggestions.append("- Add certifications, achievements, or community contributions.")

if score_breakdown["Projects"] == 0:
    suggestions.append("- Include at least one project with real-world impact.")

if score_breakdown["Experience"] == 0:
    suggestions.append("- Add any internships, freelance, or full-time experience.")

if "summary" not in resume_json:
    suggestions.append("- Add a professional summary at the top of your resume.")

if len(resume_text) > 4000:
    suggestions.append("- Consider condensing content to 1–2 pages.")

# Dynamic Suggestion Based on Role Mismatch
if "poor alignment" in alignment_rating.lower() or "moderate alignment" in alignment_rating.lower():
    missing_keywords = [kw for kw in keywords if kw not in matched_skills]
    if missing_keywords:
        top_missing = ", ".join(missing_keywords[:5])
        suggestions.append(f"- To align better with a '{selected_role}' role, consider learning: {top_missing}")

if suggestions:
    for s in suggestions:
        st.markdown(f"🔹 {s}")
else:
    st.success(" No major suggestions. Your resume looks well structured!")


# Spelling & Grammar
st.subheader(" Spelling & Grammar Suggestions")
with st.spinner("Analyzing..."):
    grammar_suggestions = grammar_and_spelling_feedback(resume_text)
    for g in grammar_suggestions:
        st.markdown(f"- {g}")

# Score Chart
st.subheader(" Visual Score Chart")
data = [{"index": k, "score": v} for k, v in score_breakdown.items()]
chart = alt.Chart(alt.Data(values=data)).mark_bar().encode(
    x="index:N",
    y="score:Q",
    color=alt.Color("index:N", legend=None)
).properties(width=600)
st.altair_chart(chart, use_container_width=True)





