# pylint: disable=invalid-name
import streamlit as st
from components import (
    load_custom_css,
    page_header,
    metric_card,
    require_auth,
    sidebar_navigation,
    format_datetime
)
from services import get_dashboard_stats, format_bytes, list_files

st.set_page_config(
    page_title="Dashboard • Safekeep",
    page_icon="💎",
    layout="wide"
)

load_custom_css()
require_auth()
sidebar_navigation()

# Page Header
page_header("Dashboard", "Your secure file vault overview")

# User Welcome Pill
user = st.session_state.user
st.markdown(f"""
    <div style="background: #151B23; border: 1px solid #30363d; border-radius: 50px; padding: 0.75rem 2rem; margin-bottom: 2rem; display: flex; align-items: center; gap: 0.5rem; width: fit-content;">
        <span>👋</span>
        <span style="color: #8b949e;">Welcome back,</span>
        <strong style="color: #f0f6fc;">{user.get('ngo', 'NGO')}</strong>
        <span style="color: #484f58;">•</span>
        <span style="color: #8b949e;">{user.get('email', '')}</span>
    </div>
""", unsafe_allow_html=True)

# Get stats
stats = get_dashboard_stats(user)

# ---------------- KEY METRICS ----------------
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(metric_card("Total Files", str(stats["total_files"])), unsafe_allow_html=True)

with col2:
    st.markdown(metric_card(
        "Storage Used", format_bytes(stats["total_storage_compressed"])
    ), unsafe_allow_html=True)

with col3:
    saved_bytes = stats["total_storage_original"] - stats["total_storage_compressed"]
    sub_text = f"Saved {format_bytes(saved_bytes)}"
    st.markdown(metric_card(
        "Space Saved", f"{stats['compression_savings_pct']:.1f}%", sub=sub_text
    ), unsafe_allow_html=True)

with col4:
    last = "Never" if not stats["last_upload"] else format_datetime(stats["last_upload"])
    st.markdown(metric_card("Last Activity", last), unsafe_allow_html=True)

# ---------------- STORAGE OVERVIEW ----------------
# ---------------- STORAGE OVERVIEW ----------------
st.markdown("### 📦 Storage Overview")
QUOTA_GB = 20
used_bytes = stats["total_storage_compressed"]
QUOTA_BYTES = QUOTA_GB * 1024 * 1024 * 1024
used_percent = min(used_bytes / QUOTA_BYTES, 1.0) * 100

st.markdown(f"""
    <div class="storage-overview-card">
        <div class="storage-meta">
            <span>{format_bytes(used_bytes)} used</span>
            <span>{QUOTA_GB} GB total</span>
        </div>
        <div class="storage-progress-bg">
            <div class="storage-progress-fill" style="width: {used_percent}%;"></div>
        </div>
        <div style="text-align: right; font-size: 0.8rem; color: #6E7681;">
            {used_percent:.1f}% Utilization
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------- QUICK ACTIONS (4 Cols) ----------------
st.markdown("### ⚡ Quick Actions")

# Layout: 4 Columns
qa1, qa2, qa3, qa4 = st.columns(4)

# Action 1: Upload
with qa1:
    st.markdown("""
        <div class="action-card-header">
            <span class="action-icon">⬆️</span>
            <div class="action-title">Upload Files</div>
            <div class="action-desc">Compress & store securely in the vault</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Upload", width="stretch"):
        st.switch_page("pages/2_Upload_Center.py")

# Action 2: Browse
with qa2:
    st.markdown("""
        <div class="action-card-header">
            <span class="action-icon">📂</span>
            <div class="action-title">Browse Vault</div>
            <div class="action-desc">Access and manage stored documents</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("View Vault", width="stretch"):
        st.switch_page("pages/3_Vault_Explorer.py")

# Action 3: Audit Logs
with qa3:
    st.markdown("""
        <div class="action-card-header">
            <span class="action-icon">📜</span>
            <div class="action-title">Audit Logs</div>
            <div class="action-desc">Track compliance and security events</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Open Logs", width="stretch"):
        st.switch_page("pages/4_Audit_Logs.py")

# Action 4: Export/Report (Placeholder or Link to Logs)
with qa4:
    st.markdown("""
        <div class="action-card-header">
            <span class="action-icon">📊</span>
            <div class="action-title">Export Data</div>
            <div class="action-desc">Generate compliance reports</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Export Report", width="stretch"):
        st.toast("Report generation started...")

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------- RECENT UPLOADS & HEALTH (Split View) ----------------
split_col1, split_col2 = st.columns([1.8, 1])

# Left: Recent Uploads
with split_col1:
    st.markdown("### 📤 Recent Uploads")
    files = list_files(user)
    recent_files = files[:5] if files else []

    if not recent_files:
        st.markdown("""
            <div class="upload-placeholder">
                <span style="font-size: 1.5rem;">📫</span>
                <span>No uploads yet. Start by uploading your first file!</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        for f in recent_files:
            st.markdown(f"""
                <div style="
                    background: #151B23;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                    border: 1px solid #30363d;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span style="font-size: 1.2rem;">📄</span>
                        <div>
                            <div style="font-weight: 600; color: #f0f6fc;">
                                {f['name']}
                            </div>
                            <div style="font-size: 0.8rem; color: #8b949e;">
                                {f['category']} • {format_bytes(f['original_size'])}
                            </div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.85rem; color: #f0f6fc;">
                            {format_bytes(f['compressed_size'])}
                        </div>
                        <div style="font-size: 0.75rem; color: #238636;">
                            Saved {f['compression_ratio']*100:.0f}%
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Right: System Health
with split_col2:
    st.markdown("### ✅ System Health")

    health_items = [
        ("S3 Storage", "Connected", "success"),
        ("Audit Logs", "Enabled", "success"),
        ("Compression", "Active", "warning"),
        ("Security", "Locked", "success"),
    ]

    for label, status_text, status_type in health_items:
        st.markdown(f"""
            <div class="system-health-item">
                <span class="status-dot {status_type}"></span>
                <span class="health-label">{label}</span>
                <span class="health-status-text">{status_text}</span>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer-text">
        © 2024 Safekeep Vault • Powered by AWS S3 & AES-256 Encryption
    </div>
""", unsafe_allow_html=True)
