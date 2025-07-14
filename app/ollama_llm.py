# app/ollama_llm.py
from langchain_community.chat_models import ChatOllama

def get_ollama_llm(model: str = "llama3"):
    return ChatOllama(model=model)
