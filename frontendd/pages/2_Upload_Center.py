import streamlit as st
# NEW:
from components import (
    load_custom_css, page_header, require_auth, 
    sidebar_navigation, format_datetime, set_glass_background
)

from services import upload_file, format_bytes
import time

st.set_page_config(
    page_title="Upload Center - Safekeep NGO Vault",
    page_icon="⬆️",
    layout="wide"
)

set_glass_background()  # Add this line
load_custom_css()

require_auth()
sidebar_navigation()

# Page header
page_header("⬆️ Upload Center", "Upload and compress files securely")

# Two column layout
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📤 Upload New File")
    
    # Upload form
    with st.form("upload_form", clear_on_submit=True):
        # Category selection
        category = st.selectbox(
            "File Category",
            options=["Finance", "Donors", "Compliance", "Programs"],
            help="Select the category that best describes this file"
        )
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "xlsx", "xls", "docx", "doc", "csv", "zip", "jpg", "png"],
            help="Supported formats: PDF, Excel, Word, CSV, ZIP, Images"
        )
        
        if uploaded_file:
           st.session_state.last_uploaded_bytes = uploaded_file.getvalue()

        # Upload button
        upload_btn = st.form_submit_button("🚀 Upload & Compress", use_container_width=True)
        
        if upload_btn and uploaded_file:
            # Progress container
            progress_container = st.container()
            
            with progress_container:
                st.markdown("### 🔄 Processing Upload")
                
                # Step 1: Uploading
                st.markdown("""
                    <div class="progress-step active">
                        <div class="step-icon">⬆️</div>
                        <div class="step-label">Uploading file...</div>
                    </div>
                """, unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate upload progress
                for i in range(25):
                    time.sleep(0.02)
                    progress_bar.progress((i + 1) * 4)
                    status_text.text(f"Uploading... {(i + 1) * 4}%")
                
                # Step 2: Compressing
                st.markdown("""
                    <div class="progress-step active">
                        <div class="step-icon">🗜️</div>
                        <div class="step-label">Compressing file...</div>
                    </div>
                """, unsafe_allow_html=True)
                
                for i in range(25, 50):
                    time.sleep(0.02)
                    progress_bar.progress((i + 1) * 2)
                    status_text.text(f"Compressing... {(i + 1) * 2}%")
                
                # Step 3: Storing in S3
                st.markdown("""
                    <div class="progress-step active">
                        <div class="step-icon">☁️</div>
                        <div class="step-label">Storing in AWS S3...</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Perform actual upload
                file_size = uploaded_file.size
                result = upload_file(
                    uploaded_file.name,
                    file_size,
                    category,
                    st.session_state.user,
                    uploaded_file.getvalue()
                )
                
                for i in range(50, 100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                    status_text.text(f"Finalizing... {i + 1}%")
                
                # Step 4: Complete
                st.markdown("""
                    <div class="progress-step complete">
                        <div class="step-icon">✅</div>
                        <div class="step-label">Upload complete!</div>
                    </div>
                """, unsafe_allow_html=True)
                
                progress_bar.progress(100)
                status_text.empty()
                
                # Show compression results
                st.markdown("---")
                st.markdown("### 📊 Compression Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Original Size",
                        format_bytes(result['original_size'])
                    )
                
                with col2:
                    st.metric(
                        "Compressed Size",
                        format_bytes(result['compressed_size'])
                    )
                
                with col3:
                    savings_pct = result['compression_ratio'] * 100
                    st.metric(
                        "Space Saved",
                        f"{savings_pct:.1f}%",
                        delta=f"-{format_bytes(result['original_size'] - result['compressed_size'])}"
                    )
                
                st.success(f"✅ **{uploaded_file.name}** uploaded successfully to **{category}** category!")
                
                st.markdown(f"""
                    **File Details:**
                    - **S3 Path:** `{result['s3_path']}`
                    - **Upload Time:** {format_datetime(result['uploaded_at'])}
                    - **Uploaded By:** {result['uploaded_by']}
                """)
                
                # Store file info for action buttons outside form
                st.session_state.last_uploaded_file = uploaded_file.name
                st.session_state.last_upload_category = category
                st.session_state.show_upload_actions = True
        
        elif upload_btn and not uploaded_file:
            st.error("Please select a file to upload")
    
    # Action buttons OUTSIDE the form
    if st.session_state.get('show_upload_actions', False):
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📁 View in Vault Explorer", key="view_vault_after_upload", use_container_width=True):
                st.switch_page("pages/3_Vault_Explorer.py")
        with col_b:
            if st.button("⬆️ Upload Another File", key="upload_another", use_container_width=True):
                st.session_state.show_upload_actions = False
                st.rerun()

with col_right:
    st.markdown("### 📋 Upload Guidelines")
    
    st.markdown("""
        <div class="feature-card">
            <h4>✅ Supported Formats</h4>
            <ul style="text-align: left; margin-left: 1rem;">
                <li>Documents: PDF, DOCX, DOC</li>
                <li>Spreadsheets: XLSX, XLS, CSV</li>
                <li>Images: JPG, PNG</li>
                <li>Archives: ZIP</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="feature-card">
            <h4>🗜️ Compression Info</h4>
            <p>Files are automatically compressed using industry-standard algorithms:</p>
            <ul style="text-align: left; margin-left: 1rem;">
                <li>PDF: 40-60% savings</li>
                <li>Images: 50-70% savings</li>
                <li>Documents: 30-50% savings</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="feature-card">
            <h4>🔒 Security</h4>
            <p>All uploads are:</p>
            <ul style="text-align: left; margin-left: 1rem;">
                <li>Encrypted in transit (TLS 1.3)</li>
                <li>Encrypted at rest (AES-256)</li>
                <li>Logged for audit purposes</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="feature-card">
            <h4>📂 Categories</h4>
            <p><strong>Finance:</strong> Financial reports, budgets<br>
            <strong>Donors:</strong> Donor information, receipts<br>
            <strong>Compliance:</strong> Certificates, audits<br>
            <strong>Programs:</strong> Project reports, data</p>
        </div>
    """, unsafe_allow_html=True)

# Upload history
st.markdown("---")
st.markdown("### 📜 Recent Uploads")

from services import list_files

recent_files = list_files(st.session_state.user)[:5]  # Last 5 uploads

if recent_files:
    for file in recent_files:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{file['name']}**")
            st.caption(f"📂 {file['category']}")
        
        with col2:
            st.markdown(f"**{format_bytes(file['compressed_size'])}**")
            st.caption("Compressed")
        
        with col3:
            savings = file['compression_ratio'] * 100
            st.markdown(f"**{savings:.0f}%**")
            st.caption("Saved")
        
        with col4:
            st.caption(format_datetime(file['uploaded_at']))
        
        st.markdown("---")
else:
    st.info("No files uploaded yet")