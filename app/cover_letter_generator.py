# app/cover_letter_generator.py
from typing import Any
from app.groq_llm import get_groq_llm
from langchain_core.prompts import PromptTemplate

def generate_cover_letter(resume: Any, job_description: str, company: str, job_title: str, tone: str, paragraphs: str) -> str:
    summary = resume.get("summary", "")
    skills = ", ".join(resume.get("skills", []))

    # Safe handling for education
    education_list = resume.get("education", [])
    if education_list and isinstance(education_list[0], dict):
        education = education_list[0].get("degree", "your degree")
    else:
        education = "your degree"

    prompt = PromptTemplate(
        input_variables=["job_title", "company", "skills", "education", "summary", "job_description", "tone", "paragraphs"],
        template="""
You are an expert career coach and resume writer.

Write a {paragraphs} cover letter for the role of {job_title} at {company}, using a {tone} tone.

Resume Info:
- Skills: {skills}
- Education: {education}
- Summary: {summary}

Match it to the job description:
{job_description}

Keep it professional, customized, and well-structured.
"""
    )

    llm = get_groq_llm()

    # Preferred pipeline usage (PromptTemplate | llm)
    try:
        chain = prompt | llm
        result = chain.invoke({
            "job_title": job_title,
            "company": company,
            "skills": skills,
            "education": education,
            "summary": summary,
            "job_description": job_description,
            "tone": tone,
            "paragraphs": paragraphs
        })
    except Exception:
        # Fallback: format prompt and call LLM directly
        try:
            final_prompt = prompt.format(
                job_title=job_title,
                company=company,
                skills=skills,
                education=education,
                summary=summary,
                job_description=job_description,
                tone=tone,
                paragraphs=paragraphs
            )
            resp = llm(final_prompt)
            result = resp
        except Exception as e:
            return f"Error calling LLM: {e}"

    # Normalize to string
    if isinstance(result, dict):
        return result.get("output_text") or result.get("text") or str(result)
    return str(result)
