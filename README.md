
An AI-powered resume companion that helps users upload and analyze their resumes, generate tailored cover letters, simulate interviews, and evaluate ATS (Applicant Tracking System) scores — all using **open-source LLMs, LangChain, FAISS**, and modern NLP pipelines.

---

## 🚀 Features

- 📄 Upload PDF resume and extract structured JSON data
- 🤖 Chat with your resume using RAG (Retrieval-Augmented Generation)
- ✍️ Generate personalized cover letters based on job description
- 🎯 Practice mock interviews with LLM evaluation and scoring
- 📊 Get ATS compatibility score and improvement suggestions
- ✅ Export cover letter as TXT, DOCX, or PDF

---

## ⚙️ Tech Stack

| Component           | Tool / Library                                      |
|---------------------|-----------------------------------------------------|
| **UI**              | Streamlit                                           |
| **PDF Parsing**     | PyMuPDF, OCR (pytesseract)                          |
| **Resume Structuring** | LangChain + Groq LLM (LLaMA3-8B-8192)           |
| **Cover Letter LLM**| Groq API                                            |
| **Chatbot (RAG)**   | HuggingFace Embeddings + FAISS                     |
| **Embeddings**      | `sentence-transformers/all-MiniLM-L6-v2`           |
| **Vector DB**       | FAISS                                               |
| **Interview QA**    | LangChain QA Chain + PromptTemplate                |
| **ATS Scoring**     | Custom scoring logic + JD keyword matcher          |
| **Grammar Checker** | TextGears API                                       |

---

##  How It Works

1. **Upload Resume**  
   Upload a `.pdf` resume file. Text is extracted using PyMuPDF and OCR (if needed).

2. **Resume Parsing**  
   Parsed using LangChain + LLaMA3 to structured JSON (name, email, skills, experience, etc.)

3. **Chatbot (Q&A)**  
   Resume text embedded using HuggingFace, stored in FAISS vector store.  
   Groq LLM answers user questions using top-k relevant chunks.

4. **Cover Letter Generator**  
   User enters job title, company, tone, etc.  
   LLM generates a customized, editable letter.

5. **Interview Questions**  
   LLM generates 10 technical & 10 behavioral questions.  
   Users answer and get feedback: score, ideal answer, suggestions.

6. **ATS Insights**  
   Matches resume content with job keywords.  
   Scores based on content sections + alignment.  
   Uses LLM for summary evaluation + TextGears for grammar.

---

## 📂 Project Structure

📂 app/
├── resume_parser.py               # Extracts raw text from PDF (OCR fallback)
├── structured_extractor.py       # LLM: Converts resume text → JSON
├── cover_letter_generator.py     # LLM: Cover letter generation
├── interview_question_gen.py     # LLM: Interview Q generator
├── ats_score.py                  # ATS score calculation logic
├── jd_keywords.py                # Predefined keywords per job role
├── rag_chatbot.py                # Vector DB + retriever logic
├── groq_llm.py / ollama_llm.py   # Groq / local LLM loader
├── utils.py                      # (Optional) Helper functions

📂 pages/
├── 1_Upload_Resume.py            # Resume upload & JSON extraction
├── 2_Chatbot_QA.py               # Resume chatbot using RAG
├── 3_Cover_Letter.py             # Cover letter generator UI
├── 4_Interview_Questions.py      # Q&A evaluator with score
├── 5_ATS_Insights.py             # ATS checker and resume analysis

main.py                           # Streamlit entry point with navigation




---

##  Installation & Run Locally

```bash
git clone https://github.com/your-username/ai-resume-assistant.git
cd ai-resume-assistant
pip install -r requirements.txt
streamlit run main.py
```
 Make sure to set your Groq API key in groq_llm.py.


##  Demo

👉 [Click to watch the demo](https://user-images.githubusercontent.com/.../demo.mp4)


## LLM Prompting (LangChain)
LLMChain: For cover letter and Q&A feedback

PromptTemplate: Custom system prompts for structured JSON, mock scores, etc.

ConversationalRetrievalChain: For resume chatbot with memory

RetrievalQA: Simple RAG fallback model

