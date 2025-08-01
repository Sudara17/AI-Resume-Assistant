import streamlit as st

st.set_page_config(page_title="AI Resume Assistant", layout="wide")

# Title and Subheading
st.title("AI Resume Assistant")
st.markdown("Welcome to your all-in-one resume support system. Choose a feature below to get started!")

# Sidebar Navigation
with st.sidebar:
    st.header("Navigate")
    st.page_link("pages/1_Upload_Resume.py", label=" Upload Resume")
    st.page_link("pages/2_Chatbot_QA.py", label=" Chatbot")
    st.page_link("pages/4_Interview_Questions.py", label=" Interview Questions")
    st.page_link("pages/5_ATS_Insights.py", label=" ATS Insights & Resume Score")
    st.page_link("pages/3_Cover_Letter.py", label=" Cover Letter Generator")

# CSS Styling
st.markdown("""
    <style>
    .horizontal-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 2rem;
        justify-content: center;
        margin-top: 3rem;
    }

    .stLinkButton {
        display: inline-block;
        width: 270px;
        height: 110px;
        text-align: center;
        padding-top: 2.8rem;
        border-radius: 18px;
        background-color: #f4f6fa;
        border: 1px solid #e0e0e0;
        font-size: 1.3rem;
        font-weight: 600;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        text-decoration: none;
        color: black;
        transition: all 0.3s ease;
    }

    .stLinkButton:hover {
        background-color: #e6f0ff;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.1);
        transform: translateY(-3px);
        border-color: #b3cde0;
    }

    @media (max-width: 768px) {
        .horizontal-buttons {
            flex-direction: column;
            align-items: center;
        }

        .stLinkButton {
            width: 90vw;
            height: 100px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Button-style Links (using <a> as custom buttons)
st.markdown('<div class="horizontal-buttons">', unsafe_allow_html=True)

st.markdown("""
<a href="pages/1_Upload_Resume.py" class="stLinkButton"> Upload Resume</a>
<a href="pages/2_Chatbot_QA.py" class="stLinkButton"> Chatbot</a>
<a href="pages/3_Cover_Letter.py" class="stLinkButton"> Cover Letter</a>
<a href="pages/4_Interview_Questions.py" class="stLinkButton"> Interview Qs</a>
<a href="pages/5_ATS_Insights.py" class="stLinkButton"> ATS Insights</a>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
