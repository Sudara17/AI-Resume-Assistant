import streamlit as st

st.set_page_config(page_title="AI Resume Assistant", layout="wide")

# Title and Subheading
st.title("AI Resume Assistant")
st.markdown("Welcome to your all-in-one resume support system. Choose a feature below to get started!")

# Sidebar Navigation
with st.sidebar:
    st.header("Navigate")
    st.page_link("pages/1_Upload_Resume.py", label="Upload Resume")
    st.page_link("pages/2_Chatbot_QA.py", label="Chatbot")
    st.page_link("pages/4_Interview_Questions.py", label="Interview Questions")
    st.page_link("pages/5_ATS_Insights.py", label="ATS Insights & Resume Score")
    st.page_link("pages/3_Cover_Letter.py", label="Cover Letter Generator")
 
#  CSS to make the buttons larger and nicely styled
st.markdown("""
    <style>
    .horizontal-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 2rem;
        justify-content: center;
        margin-top: 3rem;
    }

    .stButton > button {
        width: 270px;         /* Wider button */
        height: 110px;        /* Taller button */
        border-radius: 18px;
        background-color: #f4f6fa;
        border: 1px solid #e0e0e0;
        font-size: 1.3rem;     /* Larger text */
        font-weight: 600;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
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

        .stButton > button {
            width: 90vw;
            height: 100px;
        }
    }
    </style>
""", unsafe_allow_html=True)

#  Button Layout – One row
st.markdown('<div class="horizontal-buttons">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Upload Resume"):
        st.switch_page("pages/1_Upload_Resume.py")

with col2:
    if st.button("Chatbot"):
        st.switch_page("pages/2_Chatbot_QA.py")
        
with col1:
    if st.button("Cover Letter"):
        st.switch_page("pages/3_Cover_Letter.py")


with col3:
    if st.button("Interview Questions"):
        st.switch_page("pages/4_Interview_Questions.py")

with col4:
    if st.button("ATS"):
        st.switch_page("pages/5_ATS_Insights.py")


st.markdown('</div>', unsafe_allow_html=True)






