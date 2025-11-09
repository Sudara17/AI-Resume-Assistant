from langchain_groq import ChatGroq
import os

def get_groq_llm(model="llama-3.1-8b-instant"):
    return ChatGroq(temperature=0.3, model=model, api_key=os.environ.get("GROQ_API_KEY"), max_retries=2)
