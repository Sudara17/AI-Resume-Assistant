# app/rag_chatbot.py
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import pickle
import os

def build_vectorstore_from_text(resume_text):
    os.makedirs("data", exist_ok=True)
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}  
)
    with open("data/text_chunks.pkl", "wb") as f:
        pickle.dump([resume_text], f)
    db = FAISS.from_texts([resume_text], embedding=embeddings)
    with open("data/resume_embeddings.pkl", "wb") as f:
        pickle.dump(db, f)

def get_rag_qa_chain(api_key):  
    with open("data/resume_embeddings.pkl", "rb") as f:
        db = pickle.load(f)
    retriever = db.as_retriever()
    llm = ChatGroq(api_key=api_key, model_name="llama3-8b-8192")
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)



