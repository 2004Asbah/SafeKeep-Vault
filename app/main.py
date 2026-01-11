import streamlit as st
import boto3
from PIL import Image
import io
import base64

# --- CSS: Fixed for bg.png and Transparent Branding ---
def set_final_style(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    
    st.markdown(
        f"""
        <style>
        /* Set Background using PNG format */
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* REMOVE WHITE BOX: Total transparency */
        [data-testid="stAppViewContainer"] {{
            background-color: transparent !important;
        }}

        /* Clean up UI elements */
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        /* Professional Typography */
        .main-title {{
            font-size: 55px !important;
            font-weight: 900 !important;
            color: #0F172A; 
            text-align: center;
            margin-top: -30px;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        }}

        .sub-text {{
            font-size: 22px !important;
            color: #334155;
            text-align: center;
            font-weight: 600;
            margin-bottom: 40px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- APP START ---
st.set_page_config(page_title="SafeKeep Vault", page_icon="🛡️", layout="wide")

# Apply custom styles with the .png extension
try:
    set_final_style("app/bg.png")
except FileNotFoundError:
    st.error("Check your folder! Looking for 'app/bg.png' but could not find it.")

# --- BRANDING SECTION ---
col1, col2, col3 = st.columns([1, 0.6, 1]) # Tightened center column for logo
with col2:
    try:
        st.image("app/logo.png", use_container_width=True)
    except:
        st.markdown("<h1 style='text-align:center;'>🛡️</h1>", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">SafeKeep NGO Vault</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Secure, Low-Bandwidth Document Archiving for Humanitarian Aid</p>', unsafe_allow_html=True)

# --- UPLOADER BOX ---
st.markdown("""
    <style>
    .stFileUploader {
        background-color: rgba(255, 255, 255, 0.5); /* Semi-transparent uploader */
        padding: 30px;
        border-radius: 20px;
        max-width: 700px;
        margin: auto;
        border: 2px dashed #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload sensitive document", type=["jpg", "png", "pdf"])

# (Keep your Boto3/S3 logic below)