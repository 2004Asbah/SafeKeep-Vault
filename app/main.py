import streamlit as st
import boto3
from PIL import Image
import io
import base64
import pandas as pd
from datetime import datetime
from botocore.exceptions import ClientError

# --- CONFIGURATION ---
S3_BUCKET_NAME = "safekeep-ngo-vault-149575e8" # Ensure this matches your Terraform bucket name
AWS_REGION = "us-east-1"

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'ngo_name' not in st.session_state:
    st.session_state['ngo_name'] = ""
if 'ngo_owner' not in st.session_state:
    st.session_state['ngo_owner'] = ""

# --- CSS: Preserving your specific styling ---
def set_final_style(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            [data-testid="stAppViewContainer"] {{
                background-color: transparent !important;
            }}
            header {{visibility: hidden;}}
            footer {{visibility: hidden;}}

            .main-title {{
                font-size: 50px !important;
                font-weight: 900 !important;
                color: #0F172A; 
                text-align: center;
                margin-top: -30px;
                text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
            }}

            .sub-text {{
                font-size: 20px !important;
                color: #334155;
                text-align: center;
                font-weight: 600;
                margin-bottom: 30px;
            }}
            
            .login-box {{
                background-color: rgba(255, 255, 255, 0.85);
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
            }}

            .stMetric {{
                background-color: rgba(255, 255, 255, 0.6);
                padding: 15px;
                border-radius: 10px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("Background image not found. Using default background.")

# --- HELPER FUNCTIONS ---
def get_s3_client():
    return boto3.client('s3')

def list_vault_files():
    s3 = get_s3_client()
    try:
        # Search for files specifically for this NGO
        prefix = f"uploads/{st.session_state['ngo_name']}/"
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
        return response.get('Contents', [])
    except:
        return []

def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    img_io = io.BytesIO()
    # Save as JPEG with 60% quality for low-bandwidth NGO efficiency
    img.save(img_io, format='JPEG', quality=60, optimize=True)
    return img_io.getvalue()

def create_presigned_url(bucket_name, object_name, expiration=600):
    """Generate a temporary secure download link (valid for 10 mins)"""
    s3_client = get_s3_client()
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError:
        return None
    return response

# --- APP START ---
st.set_page_config(page_title="SafeKeep Vault", page_icon="🛡️", layout="wide")
set_final_style("app/bg.png")

# --- LOGIN LOGIC ---
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        try:
            st.image("app/logo.png", width=120)
        except:
            st.markdown("<h1 style='text-align:center;'>🛡️</h1>", unsafe_allow_html=True)
            
        st.markdown('<h1 class="main-title">Vault Access</h1>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            name = st.text_input("NGO Organization Name")
            owner = st.text_input("Representative Name")
            key = st.text_input("Access Key", type="password")
            
            if st.button("Unlock Secure Vault"):
                if key == "admin123":
                    st.session_state['logged_in'] = True
                    st.session_state['ngo_name'] = name
                    st.session_state['ngo_owner'] = owner
                    st.rerun()
                else:
                    st.error("Invalid Key")
            st.markdown('</div>', unsafe_allow_html=True)

# --- AUTHENTICATED DASHBOARD ---
else:
    # Sidebar
    st.sidebar.image("app/logo.png", width=100)
    st.sidebar.markdown(f"### 🏢 {st.session_state['ngo_name']}")
    st.sidebar.markdown(f"**User:** {st.session_state['ngo_owner']}")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.markdown('<h1 class="main-title">SafeKeep NGO Vault</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-text">Authorized Archive for {st.session_state["ngo_name"]}</p>', unsafe_allow_html=True)

    # 1. METRICS
    s3_files = list_vault_files()
    total_size_kb = sum([obj['Size'] for obj in s3_files]) / 1024
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Documents Stored", len(s3_files))
    m2.metric("Vault Weight", f"{total_size_kb:.1f} KB")
    m3.metric("Data Efficiency", "Compressed", delta="Optimized")

    st.divider()

    # 2. UPLOAD WITH FOLDERS
    st.header("📤 Secure New Document")
    
    u_col1, u_col2 = st.columns([1, 2])
    with u_col1:
        # FEATURE 1: Project-based organization
        project_folder = st.selectbox(
            "Target Project Folder", 
            ["Legal_Docs", "Field_Reports", "Beneficiary_Data", "Financials", "Identity_Cards"]
        )
    with u_col2:
        uploaded_file = st.file_uploader("Select Image (JPG/PNG)", type=["jpg", "png", "jpeg"])

    if uploaded_file and st.button("Encrypt & Secure to Cloud"):
        with st.spinner("Processing for NGO efficiency..."):
            compressed_data = compress_image(uploaded_file)
            
            s3 = get_s3_client()
            # Dynamic Folder Pathing
            file_path = f"uploads/{st.session_state['ngo_name']}/{project_folder}/{uploaded_file.name}"
            
            s3.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=file_path,
                Body=compressed_data,
                Metadata={'NGO_Owner': st.session_state['ngo_owner'], 'Project': project_folder}
            )
            st.success(f"Archived successfully in {project_folder} folder!")
            st.rerun()

    st.divider()

    # 3. VAULT EXPLORER WITH SECURE DOWNLOADS
    st.header("🔍 Vault Explorer")
    search_query = st.text_input("Filter documents by name...")

    if s3_files:
        # Column headers
        h1, h2, h3, h4 = st.columns([3, 2, 2, 1])
        h1.markdown("**File Name**")
        h2.markdown("**Project Folder**")
        h3.markdown("**Date Modified**")
        h4.markdown("**Action**")

        for obj in s3_files:
            file_key = obj['Key']
            parts = file_key.split('/')
            
            # Extract folder and filename from path
            # Path format: uploads/NGO_Name/Folder/Filename.jpg
            display_folder = parts[-2] if len(parts) > 2 else "Root"
            display_name = parts[-1]
            
            if search_query.lower() in display_name.lower():
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                c1.write(display_name)
                c2.info(display_folder)
                c3.write(obj['LastModified'].strftime("%Y-%m-%d"))
                
                # FEATURE 2: Temporary secure download link
                download_url = create_presigned_url(S3_BUCKET_NAME, file_key)
                if download_url:
                    c4.markdown(f'[Download]({download_url})', unsafe_allow_html=True)
    else:
        st.info("Vault is currently empty.")