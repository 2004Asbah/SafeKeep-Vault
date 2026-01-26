import streamlit as st
from components import (
    load_custom_css,
    page_header,
    metric_card,
    require_auth,
    sidebar_navigation,
    format_datetime,
    empty_state,
    set_glass_background
)
from services import get_dashboard_stats, list_audit_logs, format_bytes, list_files

st.set_page_config(
    page_title="Dashboard • Safekeep",
    page_icon="💎",
    layout="wide"
)

# Glassmorphism setup
set_glass_background()
load_custom_css()

# Auth + Sidebar
require_auth()
sidebar_navigation()

# Header
page_header("📊 Dashboard", "Your secure file vault overview")

# User info
user = st.session_state.user
st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.2);
    ">
    <p style="margin: 0; font-size: 0.9rem; color: rgba(255,255,255,0.9);">
        👋 Welcome back, <strong>{user['ngo']}</strong> • {user['email']}
    </p>
    </div>
""", unsafe_allow_html=True)

# Get statistics
stats = get_dashboard_stats(user)

# ---------------- GLASS METRICS ROW ----------------
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(metric_card("Total Files", str(stats["total_files"]), icon="📁"), unsafe_allow_html=True)

with col2:
    st.markdown(metric_card("Storage Used", format_bytes(stats["total_storage_compressed"]), icon="💾"), unsafe_allow_html=True)

with col3:
    saved_bytes = stats["total_storage_original"] - stats["total_storage_compressed"]
    st.markdown(
        metric_card(
            "Space Saved",
            f"{stats['compression_savings_pct']:.1f}%",
            delta=f"Saved {format_bytes(saved_bytes)}",
            icon="🗜️",
        ),
        unsafe_allow_html=True,
    )

with col4:
    last_upload_text = "Never" if not stats["last_upload"] else format_datetime(stats["last_upload"])
    st.markdown(metric_card("Last Activity", last_upload_text, icon="⏱️"), unsafe_allow_html=True)

# ---------------- STORAGE QUOTA - GLASS BAR ----------------
st.markdown("### 📦 Storage Overview")
quota_gb = 20
quota_bytes = quota_gb * 1024 * 1024 * 1024
used_bytes = stats["total_storage_compressed"]
used_percent = min(used_bytes / quota_bytes, 1.0)

# Glass progress bar
st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
    ">
        <div style="
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            height: 20px;
            margin-bottom: 0.5rem;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, #4361ee, #7209b7);
                width: {used_percent*100}%;
                height: 100%;
                border-radius: 10px;
                transition: width 0.5s ease;
            "></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
            <span>{format_bytes(used_bytes)} used</span>
            <span>{quota_gb} GB total</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------- GLASS QUICK ACTIONS ----------------
st.markdown("### ⚡ Quick Actions")
qa1, qa2, qa3, qa4 = st.columns(4)

with qa1:
    st.markdown("""
        <div class="quick-action-card">
            <h4>⬆️ Upload Files</h4>
            <p>Compress & store securely</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Upload", key="go_to_upload_1", use_container_width=True):
        st.switch_page("pages/2_Upload_Center.py")

with qa2:
    st.markdown("""
        <div class="quick-action-card">
            <h4>📁 Browse Vault</h4>
            <p>Access stored documents</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("View Vault", key="view_vault_1", use_container_width=True):
        st.switch_page("pages/3_Vault_Explorer.py")

with qa3:
    st.markdown("""
        <div class="quick-action-card">
            <h4>📜 Audit Logs</h4>
            <p>Compliance tracking</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Open Logs", key="open_logs_1", use_container_width=True):
        if user.get('role') == 'admin':
            st.switch_page("pages/4_Audit_Logs.py")
        else:
            st.error("Access restricted to Admins")

with qa4:
    st.markdown("""
        <div class="quick-action-card">
            <h4>📊 Export Data</h4>
            <p>Generate reports</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Export Report", key="export_report_1", use_container_width=True):
        st.info("📊 Report export feature coming soon!")

st.markdown("---")

# ---------------- RECENT UPLOADS + ACTIVITY ----------------
left, right = st.columns([2, 1])

with left:
    st.markdown("### 📤 Recent Uploads")
    files = list_files(user)
    recent_files = files[:5] if files else []
    
    if recent_files:
        for f in recent_files:
            savings = f["compression_ratio"] * 100
            st.markdown(f"""
                <div class="activity-item">
                    <div>📄 <strong>{f['name']}</strong> • <span class="activity-user">{f['category']}</span></div>
                    <div class="activity-time">
                        {format_datetime(f['uploaded_at'])} • Saved {savings:.0f}% • {format_bytes(f['compressed_size'])}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 No uploads yet. Start by uploading your first file!")

with right:
    st.markdown("### ✅ System Health")
    
    health_items = [
        ("🟢 S3 Storage", "Connected"),
        ("🟢 Audit Logs", "Enabled"),
        ("🟡 Compression", "Active"),
        ("🟢 Security", "Locked"),
    ]
    
    for icon, text in health_items:
        st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(5px);
                border-radius: 8px;
                padding: 0.75rem 1rem;
                margin-bottom: 0.5rem;
                border: 1px solid rgba(255,255,255,0.1);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            ">
                <span style="font-size: 1.25rem;">{icon}</span>
                <span>{text}</span>
            </div>
        """, unsafe_allow_html=True)

# ---------------- RECENT ACTIVITY ----------------
st.markdown("---")
st.markdown("### 📝 Recent Activity")
recent_logs = list_audit_logs(user, limit=5)

if recent_logs:
    for log in recent_logs:
        action_icons = {
            'UPLOAD': '⬆️',
            'DELETE': '🗑️',
            'DOWNLOAD': '⬇️',
            'LOGIN': '🔓',
            'LOGIN_FAILED': '🔒',
            'REGISTER': '📝'
        }
        icon = action_icons.get(log['action'], 'ℹ️')
        
        st.markdown(
            f"""
            <div class="activity-item">
                <div>{icon} <span class="activity-user">{log['user']}</span>
                {log['action'].lower()} {f"<strong>{log['target']}</strong>" if log['target'] != 'System' else ''}</div>
                <div class="activity-time">{format_datetime(log['timestamp'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    empty_state("No recent activity", "📝")

# ---------------- STORAGE BREAKDOWN ----------------
st.markdown("---")
st.markdown("### 📂 Storage by Category")
files = list_files(user)

if files:
    category_stats = {}
    for f in files:
        cat = f["category"]
        if cat not in category_stats:
            category_stats[cat] = {"count": 0, "size": 0}
        category_stats[cat]["count"] += 1
        category_stats[cat]["size"] += f["compressed_size"]
    
    cols = st.columns(len(category_stats))
    for idx, (cat, data) in enumerate(category_stats.items()):
        with cols[idx]:
            st.metric(
                label=f"📂 {cat}",
                value=format_bytes(data["size"]),
                delta=f"{data['count']} files"
            )
else:
    st.info("📭 No files uploaded yet. Start by uploading your first file!")