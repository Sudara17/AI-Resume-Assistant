# app/structured_extractor.py
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.groq_llm import get_groq_llm
import json
import json5

def extract_resume_json(resume_text: str):
    resume_text = (resume_text or "")[:8000]

    template = """
You are an intelligent resume parser. Given the following resume content, extract and return the following in valid JSON format:

- name
- email
- phone
- location
- linkedin (if available)
- github (if available)
- summary (professional summary/intro paragraph)
- skills (list of strings)
- education (list of objects: institution, degree, year, cgpa)
- experience (list of objects: role, company, duration, description)
- certifications (list of certificates if mentioned)
- achievements (list of notable achievements if any)
- projects (list of objects: name, description, technologies used)

Strict rules:
- All values must be strings or lists of strings.
- Do not include explanations.
- Ensure it is valid JSON.
- All keys and values must follow proper JSON structure with double quotes. No numbered indexes. Just clean JSON.

Resume:
{resume_text}

JSON Output:
"""
    prompt = PromptTemplate(input_variables=["resume_text"], template=template)
    llm = get_groq_llm()  # default model set in groq_llm.py
    chain = prompt | llm | StrOutputParser()

    raw_output = chain.invoke({"resume_text": resume_text})
    print("[Raw LLM Output]", raw_output)

    parsed_json = extract_json_from_text(raw_output)
    parsed_json = ensure_all_keys(parsed_json)
    return parsed_json

def extract_json_from_text(text: str):
    stack = []
    start = None
    for i, char in enumerate(text):
        if char == '{':
            if start is None:
                start = i
            stack.append(char)
        elif char == '}':
            if stack:
                stack.pop()
                if not stack and start is not None:
                    json_candidate = text[start:i + 1]
                    try:
                        return json.loads(json_candidate)
                    except json.JSONDecodeError as e:
                        print("[JSONDecodeError]", e)
                        try:
                            return json5.loads(json_candidate)
                        except Exception as json5_err:
                            print("[json5 Failed]", json5_err)
                            return {"error": "Could not parse JSON"}
    return {"error": "No valid JSON found in response."}

def ensure_all_keys(parsed_json: dict):
    keys = [
        "name", "email", "phone", "location", "linkedin", "github", "summary",
        "skills", "education", "experience", "certifications", "achievements", "projects"
    ]
    for key in keys:
        if key not in parsed_json:
            parsed_json[key] = "" if key in [
                "name", "email", "phone", "location", "linkedin", "github", "summary"
            ] else []
    return parsed_json
