# frontend/pages/2_Chatbot_QA.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Force HF/cache downloads to /tmp on Render (writable)
os.environ["TRANSFORMERS_CACHE"] = "/tmp"
os.environ["HF_HOME"] = "/tmp"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/tmp"
os.environ["TORCH_HOME"] = "/tmp"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "/tmp"

import pickle
import streamlit as st
from typing import List, Tuple

# LangChain community vectorstore / embeddings
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Use your Groq LLM factory (centralized)
from app.groq_llm import get_groq_llm

# --- Page setup ---
st.set_page_config(page_title="Resume Chatbot", layout="wide")
st.title(" Resume-based Chatbot")

# --- Ensure resume is loaded into session (stop if not) ---
if "resume_text" not in st.session_state or "resume_filename" not in st.session_state:
    st.warning("Please upload a resume first.")
    st.stop()

resume_text = st.session_state.resume_text
resume_name = st.session_state.resume_filename
st.success(f" Loaded: {resume_name}")

# --- Vectorstore setup (persist in session_state so it's re-used across navigation) ---
if "vectorstore" not in st.session_state:
    with st.spinner("Building vectorstore..."):
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        db = FAISS.from_texts([resume_text], embedding=embeddings)
        st.session_state["vectorstore"] = db
        st.success(" Vectorstore created.")
else:
    db = st.session_state["vectorstore"]

retriever = db.as_retriever()

# --- Chat memory and messages in session_state (keeps layout identical) ---
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []  # list of (user, assistant) tuples

# --- LLM (use factory so model is centrally controlled) ---
llm = get_groq_llm()  # uses default model in app/groq_llm.py

# --- Helper: format chat history into string for prompt context ---
def format_chat_history(chat_memory: List[Tuple[str, str]]) -> str:
    if not chat_memory:
        return ""
    lines = []
    for u, a in chat_memory:
        lines.append(f"User: {u}")
        lines.append(f"Assistant: {a}")
    return "\n".join(lines)

# --- Core: answer question using retriever + LLM ---
def answer_question(question: str, chat_memory: List[Tuple[str, str]], retriever, k: int = 4) -> str:
    # 1) retrieve top-k docs
    if hasattr(retriever, "get_relevant_documents"):
        docs = retriever.get_relevant_documents(question)
    else:
        docs = retriever.similarity_search(question, k=k)

    # 2) build context
    context_parts = []
    for d in docs:
        content = getattr(d, "page_content", None) or getattr(d, "content", None) or str(d)
        context_parts.append(content.strip())
    context = "\n\n".join(context_parts).strip() or "No relevant context found in the resume."

    # 3) format chat history
    chat_history_text = format_chat_history(chat_memory)

    # 4) prompt template (short & explicit)
    prompt_text = f"""
You are an assistant that answers questions using ONLY the provided CONTEXT from a candidate's resume.
If the context doesn't contain the answer, reply: "I don't have enough information in the resume to answer that."

CONTEXT:
{context}

CHAT HISTORY:
{chat_history_text}

QUESTION:
{question}

Provide a concise, resume-focused answer.
"""

    # 5) call LLM
    try:
        # Preferred: try the LCEL pipeline if available
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate(input_variables=["text"], template="{text}")
        chain = prompt | llm
        result = chain.invoke({"text": prompt_text})
        if isinstance(result, dict):
            return result.get("output_text") or result.get("text") or str(result)
        return str(result)
    except Exception:
        # Fallback: call llm directly (some wrappers accept direct call)
        try:
            resp = llm(prompt_text)
            if isinstance(resp, dict):
                return resp.get("output_text") or resp.get("text") or str(resp)
            return str(resp)
        except Exception as e:
            return f"LLM call failed: {e}"

# --- UI: display previous messages ---
st.subheader(" Chat with your resume")
for chat in st.session_state.chat_messages:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# --- Chat input ---
prompt = st.chat_input("Ask anything about your resume...")

if prompt:
    # display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    # answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = answer_question(prompt, st.session_state.chat_memory, retriever)
            st.markdown(answer)

    # save to chat history & memory
    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
    st.session_state.chat_memory.append((prompt, answer))

# --- Clear Chat button (keeps behavior identical) ---
if st.button(" Clear Chat"):
    st.session_state.chat_messages = []
    st.session_state.chat_memory = []
    st.success("Chat cleared.")


