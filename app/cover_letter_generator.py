from app.groq_llm import get_groq_llm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def generate_cover_letter(resume, job_description, company, job_title, tone, paragraphs):
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
    chain = LLMChain(prompt=prompt, llm=llm)
    return chain.run({
        "job_title": job_title,
        "company": company,
        "skills": skills,
        "education": education,
        "summary": summary,
        "job_description": job_description,
        "tone": tone,
        "paragraphs": paragraphs
    })   