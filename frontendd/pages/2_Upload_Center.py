# pylint: disable=invalid-name
import time
import streamlit as st
from components import (
    load_custom_css, page_header, require_auth,
    sidebar_navigation, format_datetime
)
from services import upload_file, format_bytes, list_files


st.set_page_config(
    page_title="Upload Center - Safekeep NGO Vault",
    page_icon="⬆️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_custom_css()
require_auth()
sidebar_navigation()

# Page header
page_header("Upload Center", "Upload and compress files securely")

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

        # Upload button
        upload_btn = st.form_submit_button("🚀 Upload & Compress", width="stretch")

        if upload_btn and uploaded_file:
            # Use Streamlit Status Container for cleaner look
            with st.status("Processing Upload...", expanded=True) as status:
                st.write("⬆️ Uploading file...")
                time.sleep(1)

                st.write("🗜️ Compressing file...")
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)

                st.write("☁️ Storing in AWS S3...")

                # Perform actual upload
                try:
                    file_size = uploaded_file.size
                    result = upload_file(
                        uploaded_file.name,
                        file_size,
                        category,
                        st.session_state.user['email'],
                        uploaded_file.getvalue()
                    )
                    status.update(label="Upload Complete!", state="complete", expanded=False)

                    st.success(f"✅ **{uploaded_file.name}** uploaded successfully!")

                    # Compression Results
                    st.markdown("### 📊 Compression Results")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Original Size", format_bytes(result['original_size']))
                    with col2:
                        st.metric("Compressed Size", format_bytes(result['compressed_size']))
                    with col3:
                        savings_pct = result['compression_ratio'] * 100
                        saved_bytes = result['original_size'] - result['compressed_size']
                        st.metric(
                            "Space Saved",
                            f"{savings_pct:.1f}%",
                            delta=f"-{format_bytes(saved_bytes)}"
                        )

                    # Store for actions
                    st.session_state.show_upload_actions = True

                except Exception as e: # pylint: disable=broad-exception-caught
                    status.update(label="Upload Failed", state="error")
                    st.error(f"Error during upload: {str(e)}")

        elif upload_btn and not uploaded_file:
            st.error("Please select a file to upload")


    # Action buttons (Always Visible)
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📁 View in Vault Explorer", width="stretch"):
            st.switch_page("pages/3_Vault_Explorer.py")
    with col_b:
        # "Upload Another File" effectively resets the form/page
        if st.button("⬆️ Upload Another File", width="stretch"):
            st.session_state.show_upload_actions = False
            st.rerun()


with col_right:
    # Move guidelines section upward by removing top spacing
    st.markdown('<div style="margin-top: -2rem;"></div>', unsafe_allow_html=True)
    st.markdown("### 📋 Upload Guidelines")

    def info_card(title, content):
        st.markdown(f"""
            <div style="background: #151B23; border: 1px solid #30363d; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;">
                <h4 style="margin-top: 0; font-size: 1rem; color: #f0f6fc;">{title}</h4>
                <div style="font-size: 0.9rem; color: #8b949e;">{content}</div>
            </div>
        """, unsafe_allow_html=True)

    info_card("✅ Supported Formats", """
    <ul style="padding-left: 1.2rem; margin-bottom: 0;">
        <li>Documents: PDF, DOCX, DOC</li>
        <li>Spreadsheets: XLSX, XLS, CSV</li>
        <li>Images: JPG, PNG</li>
        <li>Archives: ZIP</li>
    </ul>
    """)

    info_card("🗜️ Compression Info", """
    Files are automatically compressed:
    <ul style="padding-left: 1.2rem; margin-bottom: 0;">
        <li>PDF: 40-60% savings</li>
        <li>Images: 50-70% savings</li>
        <li>Documents: 30-50% savings</li>
    </ul>
    """)

    info_card("🔒 Security", """
    <ul style="padding-left: 1.2rem; margin-bottom: 0;">
        <li>Encrypted in transit (TLS 1.3)</li>
        <li>Encrypted at rest (AES-256)</li>
        <li>Logged for audit purposes</li>
    </ul>
    """)

    info_card("📂 Categories", """
    <strong>Finance:</strong> Financial reports<br>
    <strong>Donors:</strong> Donor receipts<br>
    <strong>Compliance:</strong> Certificates<br>
    <strong>Programs:</strong> Project data
    """)

# Upload history
st.markdown("### 📜 Recent Uploads")
recent_files = list_files()[:5]

if recent_files:
    for file in recent_files:
        st.markdown(f"""
            <div style="
                background: #151B23;
                border-bottom: 1px solid #30363d;
                padding: 1rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div>
                    <div style="font-weight: 600; color: #f0f6fc;">{file['name']}</div>
                    <div style="font-size: 0.8rem; color: #8b949e;">
                        {file['category']} • {format_datetime(file['uploaded_at'])}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight: 600; color: #f0f6fc;">
                        {format_bytes(file['compressed_size'])}
                    </div>
                    <div style="font-size: 0.8rem; color: #238636;">
                        Saved {file['compression_ratio']*100:.0f}%
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("No files uploaded yet")
