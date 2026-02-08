# pylint: disable=invalid-name
import streamlit as st
from components import (
    load_custom_css, page_header, require_auth,
    sidebar_navigation, format_datetime, empty_state
)
from services import list_files, delete_file, format_bytes, get_file_content, share_file


st.set_page_config(
    page_title="Vault Explorer - Safekeep NGO Vault",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_custom_css()
require_auth()
sidebar_navigation()

# Page header
page_header("Vault Explorer", "Browse and manage your secure files")

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
files = list_files(search_query, category_filter)

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
    empty_state("No files found. Upload your first file to get started!")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬆️ Go to Upload Center", width="stretch"):
        st.switch_page("pages/2_Upload_Center.py")

# Display files
for idx, file in enumerate(files):
    # Use HTML for consistent row styling
    savings_pct = file['compression_ratio']  # Already stored as percentage
    st.markdown(f"""
                <div style="
                    background: #151B23;
                    border: 1px solid #30363d;
                    border-radius: 8px;
                    padding: 1.5rem;
                    margin-bottom: 1rem;
                ">
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        ">
            <div>
                <h3 style="margin: 0; font-size: 1.1rem; color: #f0f6fc;">
                    📄 {file['name']}
                </h3>
                <div style="color: #8b949e; font-size: 0.9rem; margin-top: 0.25rem;">
                    {file['category']} • {file['uploaded_by']}
                    <br>
                    {format_datetime(file['uploaded_at'])}
                </div>
            </div>
             <div style="text-align: right;">
                <div style="
                    background: rgba(59, 130, 246, 0.1);
                    color: #3b82f6;
                    padding: 0.2rem 0.6rem;
                    border-radius: 20px;
                    font-size: 0.8rem;
                    display: inline-block;
                ">
                    {format_bytes(file['compressed_size'])}
                </div>
                <div style="color: #238636; font-size: 0.8rem; margin-top: 0.25rem;">
                    Saved {savings_pct:.0f}%
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Actions within the card row (using Streamlit columns inside container won't work well)
    # inside HTML div so we close the div and add actions below it.
    # We can use st.container to group, but styling the container is hard.
    # We will close the HTML div, but conceptually treat the expander as attached?
    # Let's keep the HTML simple and use Streamlit for actions below.

    st.markdown("</div>", unsafe_allow_html=True) # End card

    # We put expander properly
    with st.expander(f"📋 Actions for {file['name']}"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Use session state to track download requests (lazy loading)
            download_key = f"download_requested_{file['id']}"
            
            if st.session_state.get(download_key):
                # User requested download, fetch content now
                content = get_file_content(file['id'])
                if content:
                    st.download_button(
                        label="⬇️ Download",
                        data=content,
                        file_name=file['name'],
                        mime="application/octet-stream",
                        key=f"dl_{file['id']}",
                        width="stretch"
                    )
                else:
                    st.error("Failed to fetch file")
                # Reset the state
                st.session_state[download_key] = False
            else:
                # Show button to trigger download
                if st.button("⬇️ Download", key=f"dl_btn_{file['id']}", width="stretch"):
                    st.session_state[download_key] = True
                    st.rerun()

        with col2:
            if st.button("📤 Share", key=f"share_{file['id']}", width="stretch"):
                share_url = share_file(file['id'])
                if share_url:
                    st.code(share_url, language=None)
                    st.success("🔗 Share link generated! Copy the link above.")
                    st.caption("⏰ Link expires in 1 hour")
                else:
                    st.error("Failed to generate share link")

        with col3:
            if st.button("📋 Path", key=f"path_{file['id']}", width="stretch"):
                st.code(file['s3_path'])

        with col4:
            if st.button("🗑️ Delete", key=f"del_{file['id']}", width="stretch", type="primary"):
                delete_file(file['id'], st.session_state.user)
                st.rerun()

# Summary statistics at bottom
if files:
    st.markdown("---")
    st.markdown("### 📊 Summary Statistics")

    col1, col2, col3, col4 = st.columns(4)

    total_original = sum(f['original_size'] for f in files)
    total_compressed = sum(f['compressed_size'] for f in files)
    avg_compression = (
        ((total_original - total_compressed) / total_original * 100)
        if total_original > 0 else 0
    )

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
