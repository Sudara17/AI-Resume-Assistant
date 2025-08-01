from langchain_groq import ChatGroq

def get_groq_llm(model="llama3-8b-8192"):
    return ChatGroq(
        temperature=0.3,
        model_name=model,
        api_key=os.environ.get("GROQ_API_KEY")
    )
