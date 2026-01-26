import streamlit as st
from components import (
    load_custom_css, page_header, require_auth, 
    sidebar_navigation, format_datetime, set_glass_background, empty_state
)
from services import list_files, delete_file, format_bytes, get_file_content
import pandas as pd

st.set_page_config(
    page_title="Vault Explorer - Safekeep NGO Vault",
    page_icon="📁",
    layout="wide"
)

set_glass_background()  # Add this line
load_custom_css()

require_auth()
sidebar_navigation()

# Page header
page_header("📁 Vault Explorer", "Browse and manage your secure files")

# Search and filter bar
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_query = st.text_input("🔍 Search files", placeholder="Search by filename...")

with col2:
    category_filter = st.selectbox(
        "Category",
        options=["All", "Finance", "Donors", "Compliance", "Programs"]
    )

with col3:
    sort_by = st.selectbox(
        "Sort by",
        options=["Newest First", "Oldest First", "Name A-Z", "Name Z-A", "Largest First"]
    )

# Get files based on filters
files = list_files(st.session_state.user, search_query, category_filter)

# Apply sorting
if sort_by == "Newest First":
    files = sorted(files, key=lambda x: x['uploaded_at'], reverse=True)
elif sort_by == "Oldest First":
    files = sorted(files, key=lambda x: x['uploaded_at'])
elif sort_by == "Name A-Z":
    files = sorted(files, key=lambda x: x['name'])
elif sort_by == "Name Z-A":
    files = sorted(files, key=lambda x: x['name'], reverse=True)
elif sort_by == "Largest First":
    files = sorted(files, key=lambda x: x['original_size'], reverse=True)

st.markdown("---")

# Display file count
if files:
    st.markdown(f"**{len(files)}** file(s) found")
    st.markdown("<br>", unsafe_allow_html=True)
else:
    empty_state("No files found. Upload your first file to get started!", "📭")
    if st.button("⬆️ Go to Upload Center", use_container_width=True):
        st.switch_page("pages/2_Upload_Center.py")

# Display files
for idx, file in enumerate(files):
    with st.container():
        # Main file row
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        
        with col1:
            st.markdown(f"### 📄 {file['name']}")
            st.caption(f"📂 {file['category']} | Uploaded by {file['uploaded_by']}")
        
        with col2:
            st.metric("Original", format_bytes(file['original_size']))
        
        with col3:
            st.metric("Compressed", format_bytes(file['compressed_size']))
        
        with col4:
            savings = file['compression_ratio'] * 100
            st.metric("Saved", f"{savings:.1f}%")
        
        with col5:
            st.caption("Uploaded")
            st.caption(format_datetime(file['uploaded_at']))
        
        # Action buttons in expander
        with st.expander("📋 File Details & Actions"):
            # File details
            details_col1, details_col2 = st.columns(2)
            
            with details_col1:
                st.markdown(f"""
                    **File Information:**
                    - **File ID:** `{file['id']}`
                    - **Category:** {file['category']}
                    - **Upload Date:** {format_datetime(file['uploaded_at'])}
                    - **Uploaded By:** {file['uploaded_by']}
                """)
            
            with details_col2:
                st.markdown(f"""
                    **Storage Information:**
                    - **S3 Path:** `{file['s3_path']}`
                    - **Original Size:** {format_bytes(file['original_size'])}
                    - **Compressed Size:** {format_bytes(file['compressed_size'])}
                    - **Compression Ratio:** {file['compression_ratio'] * 100:.1f}%
                """)
            
            st.markdown("---")
            
            # Action buttons
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
            
            with action_col1:
                content = get_file_content(file['id'])
                
                if content:
                    st.download_button(
                        label="⬇️ Download",
                        data=content,
                        file_name=file['name'],
                        mime="application/octet-stream", # Generic binary
                        key=f"download_{file['id']}",
                        use_container_width=True
                    )
                else:
                     st.download_button(
                        label="⬇️ Download (Missing)",
                        data=b"File content not found",
                        file_name=f"{file['name']}_missing.txt",
                        mime="text/plain",
                        key=f"download_{file['id']}",
                        use_container_width=True,
                        disabled=True
                    )
            
            with action_col2:
                if st.button(f"📤 Share", key=f"share_{file['id']}", use_container_width=True):
                    st.info("Share link generated (mock)")
            
            with action_col3:
                if st.button(f"📋 Copy Path", key=f"copy_{file['id']}", use_container_width=True):
                    st.success(f"S3 path copied to clipboard")
            
            with action_col4:
                # Delete button with confirmation
                delete_key = f"delete_{file['id']}"
                confirm_key = f"confirm_delete_{file['id']}"
                
                if delete_key not in st.session_state:
                    st.session_state[delete_key] = False
                
                if not st.session_state[delete_key]:
                    if st.button(f"🗑️ Delete", key=f"del_btn_{file['id']}", use_container_width=True):
                        st.session_state[delete_key] = True
                        st.rerun()
                else:
                    st.warning("Confirm delete?")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ Yes", key=f"yes_{file['id']}", use_container_width=True):
                            if delete_file(file['id'], st.session_state.user):
                                st.success(f"Deleted {file['name']}")
                                st.session_state[delete_key] = False
                                st.rerun()
                    with col_b:
                        if st.button("❌ No", key=f"no_{file['id']}", use_container_width=True):
                            st.session_state[delete_key] = False
                            st.rerun()
        
        st.markdown("---")

# Summary statistics at bottom
if files:
    st.markdown("### 📊 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_original = sum(f['original_size'] for f in files)
    total_compressed = sum(f['compressed_size'] for f in files)
    avg_compression = ((total_original - total_compressed) / total_original * 100) if total_original > 0 else 0
    
    with col1:
        st.metric("Total Files", len(files))
    
    with col2:
        st.metric("Original Size", format_bytes(total_original))
    
    with col3:
        st.metric("Compressed Size", format_bytes(total_compressed))
    
    with col4:
        st.metric(
            "Average Savings",
            f"{avg_compression:.1f}%",
            delta=f"-{format_bytes(total_original - total_compressed)}"
        )
    
    # Export option
    st.markdown("---")
    
    if st.button("📊 Export File List as CSV", use_container_width=False):
        # Create DataFrame
        df = pd.DataFrame([{
            'File Name': f['name'],
            'Category': f['category'],
            'Original Size (bytes)': f['original_size'],
            'Compressed Size (bytes)': f['compressed_size'],
            'Savings %': f'{f["compression_ratio"] * 100:.1f}',
            'Uploaded By': f['uploaded_by'],
            'Upload Date': f['uploaded_at'],
            'S3 Path': f['s3_path']
        } for f in files])
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="vault_files_export.csv",
            mime="text/csv"
        )