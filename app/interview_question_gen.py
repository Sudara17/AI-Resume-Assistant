# app/interview_question_gen.py
from typing import Any
from langchain_core.prompts import PromptTemplate
from app.groq_llm import get_groq_llm

def generate_interview_questions(resume_json: Any) -> str:
    resume_text = str(resume_json)[:3000]

    # NOTE: you passed a model name previously. keep same behavior but be aware
    # the model name "llama3-8b-8192" may be decommissioned (update in get_groq_llm()).
    llm = get_groq_llm("llama3-8b-8192")

    question_prompt = PromptTemplate(
        input_variables=["resume"],
        template="""
You are a senior technical recruiter. Based on the candidate's resume below, generate a set of customized interview questions ONLY related to their experience, skills, and projects. Based on the following resume, generate 10 technical and 10 behavioral interview questions.

Split the questions into two categories:
- [Technical] – related to tools, technologies, languages, projects, implementations, and problem-solving from their resume.
- [Behavioral] – related to teamwork, leadership, decision-making, communication, or challenges they've faced based on resume context.

Only ask relevant and personalized questions that make sense based on the resume. Do not ask about technologies or topics not mentioned in the resume.

Return in this format:
[Technical] Question 1  
[Behavioral] Question 2  
[Technical] Question 3  
...

Resume:
{resume}
"""
    )

    try:
        chain = question_prompt | llm
        result = chain.invoke({"resume": resume_text})
    except Exception:
        # Fallback — format and call LLM directly
        try:
            final_prompt = question_prompt.format(resume=resume_text)
            resp = llm(final_prompt)
            result = resp
        except Exception as e:
            return f"Error calling LLM: {e}"

    if isinstance(result, dict):
        return result.get("output_text") or result.get("text") or str(result)
    return str(result)
