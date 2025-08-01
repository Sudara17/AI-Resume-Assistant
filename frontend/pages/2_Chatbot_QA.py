import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import pickle

#  Setup 
st.set_page_config(page_title="Resume Chatbot", layout="wide")
st.title(" Resume-based Chatbot")

if "resume_text" not in st.session_state or "resume_filename" not in st.session_state:
    st.warning("Please upload a resume first.")
    st.stop()

resume_text = st.session_state.resume_text
resume_name = st.session_state.resume_filename
st.success(f" Loaded: {resume_name}")

# Vectorstore Setup 
if not os.path.exists("data"):
    os.makedirs("data")

vectorstore_path = "data/resume_embeddings.pkl"
if "vectorstore_built" not in st.session_state:
    with st.spinner("Building vectorstore..."):
        embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}  )
        db = FAISS.from_texts([resume_text], embedding=embeddings)
        with open(vectorstore_path, "wb") as f:
            pickle.dump(db, f)
        st.session_state.vectorstore_built = True
        st.success(" Vectorstore created.")

with open(vectorstore_path, "rb") as f:
    db = pickle.load(f)

retriever = db.as_retriever()

#  Groq LLM and Memory 
llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=os.environ.get("GROQ_API_KEY")
)

if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True
    )

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=st.session_state.chat_memory
)

# Chat Display 
st.subheader(" Chat with your resume")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Show previous messages
for chat in st.session_state.chat_messages:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# New chat input at bottom
prompt = st.chat_input("Ask anything about your resume...")

if prompt:
    # Add user message
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = qa_chain.run(prompt)
            st.markdown(response)

    # Save to chat history
    st.session_state.chat_messages.append({"role": "assistant", "content": response})

# Clear button
if st.button(" Clear Chat"):
    st.session_state.chat_messages = []
    st.session_state.chat_memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True
    )
