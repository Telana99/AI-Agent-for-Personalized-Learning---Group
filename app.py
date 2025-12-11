import streamlit as st

# --- Force Dark Mode CSS ---
st.markdown(
    """
    <style>
    /* Main background */
    .css-18e3th9 {background-color: #0e1117; color: #fafafa;}
    
    /* Sidebar background */
    .css-1d391kg {background-color: #262730; color: #fafafa;}
    
    /* Headers and text */
    h1, h2, h3, h4, h5, h6, p, span {color: #fafafa;}
    
    /* Buttons */
    .stButton>button {background-color:#1abc9c; color:white;}
    
    /* Input fields */
    .stTextInput>div>div>input {background-color:#262730; color:#fafafa;}
    
    /* Selectboxes */
    .stSelectbox>div>div>div>div {background-color:#262730; color:#fafafa;}
    
    /* Text areas */
    .stTextArea>div>div>textarea {background-color:#262730; color:#fafafa;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Redirect to login page ---
st.switch_page("pages/0_Login.py")
