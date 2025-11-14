# same imports
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import re
import html
import streamlit as st

# Your helper file
from app.interview_question_gen import generate_interview_questions
from app.groq_llm import get_groq_llm

# FIXED LangChain imports
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

st.set_page_config(page_title="Interview Questions", layout="wide")
st.title("Interview Questions Generator & Mock Practice")

# Helper Function for Consistent UI Formatting
def display_correct_answer(title, body, sub_sections=[], feedback={}):
    st.markdown("### Correct Answer:", unsafe_allow_html=True)
    st.markdown(f"<span style='font-size:20px; font-weight:bold;'>{title}</span>", unsafe_allow_html=True)
    st.markdown(body, unsafe_allow_html=True)

    for subtitle, content in sub_sections:
        st.markdown(f"<br><span style='font-size:17px; font-weight:600;'>{subtitle}</span>", unsafe_allow_html=True)
        st.markdown(content, unsafe_allow_html=True)

    st.markdown("### Evaluation Feedback:", unsafe_allow_html=True)
    st.markdown(f"""
**Score:** {feedback.get("score", "")}  
**Correct Answer:** {feedback.get("answer", "")}  
**Strengths:** {feedback.get("strengths", "")}  
**Suggestions:** {feedback.get("suggestions", "")}
""", unsafe_allow_html=True)

# Main logic
if "resume_json" not in st.session_state:
    st.warning("Please upload a resume first.")
    st.stop()

parsed_json = st.session_state["resume_json"]
mode = st.radio("Choose Interview Mode", ["Technical", "Behavioral"], horizontal=True)

if st.button("Generate Interview Questions"):
    with st.spinner("Generating questions..."):
        raw = generate_interview_questions(parsed_json)
        all_questions = re.findall(r"\[(Technical|Behavioral)\]\s+(.*)", raw)

        # Save full list
        st.session_state["interview_questions_raw"] = raw
        st.session_state.all_q = all_questions

        # Filter questions by type
        if mode == "Technical":
            st.session_state.mock_questions = [q for typ, q in all_questions if typ == "Technical"]
        elif mode == "Behavioral":
            st.session_state.mock_questions = [q for typ, q in all_questions if typ == "Behavioral"]
        else:
            st.session_state.mock_questions = [q for _, q in all_questions]

        st.session_state.current_q_index = 0
        st.session_state.mock_history = []
        st.success(f"{len(st.session_state.mock_questions)} questions loaded.")

st.divider()
st.subheader("Mock Interview Chat")

if "mock_questions" in st.session_state and st.session_state.mock_questions:
    q_index = st.session_state.current_q_index

    if q_index < len(st.session_state.mock_questions):
        current_q = st.session_state.mock_questions[q_index]
        st.markdown(f"**Q{q_index+1}:** {current_q}")

        with st.form(f"form_{q_index}"):
            user_answer = st.text_area("Your Answer", key=f"answer_{q_index}")
            submitted = st.form_submit_button("Submit Answer")

        if submitted:
            if not user_answer.strip():
                st.warning("Please enter an answer before submitting.")
                st.stop()

            with st.spinner("Evaluating your answer..."):
                llm = get_groq_llm("llama3-8b-8192")

                # Correct Answer
                correct_prompt = PromptTemplate(
                    input_variables=["question"],
                    template="""
You are a senior interviewer. Write an ideal answer to the following interview question:

Question: {question}

Give a complete and technically correct answer in markdown format.
"""
                )
                correct_chain = LLMChain(prompt=correct_prompt, llm=llm)
                correct_answer = correct_chain.run({"question": current_q})

                # Suggestion Prompt
                suggest_prompt = PromptTemplate(
    input_variables=["question", "answer", "correct_answer", "resume"],
    template="""
You are a strict technical interviewer evaluating candidate responses to interview questions. 

You must follow these grading rules:
- Score 0–2/10: If the answer is empty, gibberish, or irrelevant (e.g., "asdf", "DRD", etc.)
- Score 3–5/10: If the answer is somewhat related but lacks key technical details or clarity
- Score 6–8/10: If the answer is mostly correct, with some structure and insight, but could use more technical depth
- Score 9–10/10: If the answer is clear, complete, technically strong, and well-structured

Return the feedback in this strict format:
Score: <number>/10  
Correct Answer: <one-paragraph clear and technical ideal answer>  
Strengths: <clear strengths if any — else say “None”>  
Suggestions: <very specific, actionable feedback — no general comments>

Use only plain text (no **, no *, no markdown inside). Never give a high score to gibberish or irrelevant answers.

Question: {question}  
Candidate's Answer: {answer}  
Reference Ideal Answer: {correct_answer}  
Resume Excerpt: {resume}
"""
)


                suggest_chain = LLMChain(prompt=suggest_prompt, llm=llm)
                suggestions = suggest_chain.run({
                    "question": current_q,
                    "answer": user_answer.strip(),
                    "correct_answer": correct_answer,
                    "resume": str(parsed_json)[:1500]
                })

                # CLEANING & FORMATTING BLOCK
                cleaned_suggestions = suggestions.strip()
                cleaned_suggestions = re.sub(r"\*\*(Score:.*?)\*\*", r"\1", cleaned_suggestions)
                cleaned_suggestions = re.sub(r"\*\*(Correct Answer:.*?)\*\*", r"\1", cleaned_suggestions)
                cleaned_suggestions = re.sub(r"\*\*(Strengths:.*?)\*\*", r"\1", cleaned_suggestions)
                cleaned_suggestions = re.sub(r"\*\*(Suggestions:.*?)\*\*", r"\1", cleaned_suggestions)
                cleaned_suggestions = re.sub(r"^\s*[\*\-]\s*", "", cleaned_suggestions, flags=re.MULTILINE)

                correct_answer_lines = correct_answer.strip().splitlines()
                short_correct_answer = "\n".join(correct_answer_lines[:8])  

                # Extract individual feedback parts
                score = re.search(r"Score:\s*(\d+)/10", cleaned_suggestions)
                correct_text = re.search(r"Correct Answer:\s*(.*?)Strengths:", cleaned_suggestions, re.DOTALL)
                strengths = re.search(r"Strengths:\s*(.*?)Suggestions:", cleaned_suggestions, re.DOTALL)
                suggestions_text = re.search(r"Suggestions:\s*(.*)", cleaned_suggestions, re.DOTALL)

                display_correct_answer(
                    title=short_correct_answer.splitlines()[0] if short_correct_answer else "Correct Answer",
                    body="\n".join(short_correct_answer.splitlines()[1:]),
                    sub_sections=[],
                    feedback={
                        "score": score.group(1) if score else "",
                        "answer": correct_text.group(1).strip() if correct_text else "",
                        "strengths": strengths.group(1).strip() if strengths else "",
                        "suggestions": suggestions_text.group(1).strip() if suggestions_text else "",
                    }
                )

                # Save this to history
                st.session_state.mock_history.append({
                    "q": current_q,
                    "a": user_answer,
                    "f": cleaned_suggestions
                })

                st.session_state.current_q_index += 1
                st.rerun()

# Show feedback history
if "mock_history" in st.session_state:
    st.subheader("Previous Q&A Feedback")
    total_score = 0
    score_count = 0

    for i, entry in enumerate(st.session_state.mock_history):
        st.markdown(f"### Q{i+1}: {entry['q']}")
        st.markdown(f"**You:** {entry['a']}")
        st.markdown("### Evaluation Feedback:", unsafe_allow_html=True)
        st.markdown(entry["f"], unsafe_allow_html=True)
        st.markdown("---")

        score_match = re.search(r"Score:\s*(\d+)/10", entry["f"])
        if score_match:
            total_score += int(score_match.group(1))
            score_count += 1

    if score_count > 0:
        avg = round(total_score / score_count, 2)
        st.success(f"**Overall Score:** {total_score}/{score_count*10} ({avg}/10 average)")

# Restart
if st.button("Restart Mock Interview"):
    for key in ["mock_questions", "mock_history", "current_q_index", "interview_questions_raw"]:
        st.session_state.pop(key, None)
    st.rerun()

