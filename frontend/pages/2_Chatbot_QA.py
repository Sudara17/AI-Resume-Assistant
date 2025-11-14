# frontend/pages/2_Chatbot_QA.py
import sys, os
# ensure project root (where app/ lives) is importable on Render
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# send HF caches to /tmp (writable on Render)
os.environ["TRANSFORMERS_CACHE"] = "/tmp"
os.environ["HF_HOME"] = "/tmp"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/tmp"
os.environ["TORCH_HOME"] = "/tmp"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "/tmp"

import streamlit as st
import pickle
from typing import List, Tuple

# LangChain community vectorstore / embeddings
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# centralized LLM factory
from app.groq_llm import get_groq_llm

# --- Page setup ---
st.set_page_config(page_title="Resume Chatbot", layout="wide")
st.title(" Resume-based Chatbot")

# --- Ensure resume is loaded into session (stop if not). This should be set on Upload page. ---
if "resume_text" not in st.session_state or "resume_filename" not in st.session_state:
    st.warning("Please upload a resume first.")
    st.stop()

resume_text = st.session_state.resume_text
resume_name = st.session_state.resume_filename
st.success(f" Loaded: {resume_name}")

# --- Vectorstore: build once and keep in session_state (reliable across navigation) ---
if "vectorstore" not in st.session_state:
    with st.spinner("Building vectorstore..."):
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
            db = FAISS.from_texts([resume_text], embedding=embeddings)
            # store in session for reuse
            st.session_state["vectorstore"] = db
            st.success(" Vectorstore created.")
        except Exception as e:
            st.error(f"Failed to build embeddings/vectorstore: {e}")
            st.stop()
else:
    db = st.session_state["vectorstore"]

# Use db/retriever
db = st.session_state.get("vectorstore")
retriever = db.as_retriever()

# --- Chat memory and messages in session_state (keeps layout identical) ---
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []  # list of (user, assistant) tuples

# --- LLM ---
llm = get_groq_llm()  # uses default model in app/groq_llm.py

# --- Helpers ---
def format_chat_history(chat_memory: List[Tuple[str, str]]) -> str:
    if not chat_memory:
        return ""
    lines = []
    for u, a in chat_memory:
        lines.append(f"User: {u}")
        lines.append(f"Assistant: {a}")
    return "\n".join(lines)

def answer_question(question: str, chat_memory: List[Tuple[str, str]], retriever, k: int = 4) -> str:
    # retrieve docs
    if hasattr(retriever, "get_relevant_documents"):
        docs = retriever.get_relevant_documents(question)
    else:
        docs = retriever.similarity_search(question, k=k)

    # build context
    context_parts = []
    for d in docs:
        content = getattr(d, "page_content", None) or getattr(d, "content", None) or str(d)
        context_parts.append(content.strip())
    context = "\n\n".join(context_parts).strip() or "No relevant context found in the resume."

    # history
    chat_history_text = format_chat_history(chat_memory)

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

    # call LLM robustly
    try:
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate(input_variables=["text"], template="{text}")
        chain = prompt | llm
        result = chain.invoke({"text": prompt_text})
        if isinstance(result, dict):
            return result.get("output_text") or result.get("text") or str(result)
        return str(result)
    except Exception:
        try:
            resp = llm(prompt_text)
            if isinstance(resp, dict):
                return resp.get("output_text") or resp.get("text") or str(resp)
            return str(resp)
        except Exception as e:
            return f"LLM call failed: {e}"

# --- UI rendering: show previous messages (keeps identical UX) ---
st.subheader(" Chat with your resume")
for chat in st.session_state.chat_messages:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# chat input
prompt = st.chat_input("Ask anything about your resume...")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = answer_question(prompt, st.session_state.chat_memory, retriever)
            st.markdown(answer)

    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
    st.session_state.chat_memory.append((prompt, answer))

# Clear Chat button (same as before)
if st.button(" Clear Chat"):
    st.session_state.chat_messages = []
    st.session_state.chat_memory = []
    st.success("Chat cleared.")
